from flask import Blueprint, current_app, g, request, send_file

from ..extensions import db
from ..models import Booking, BookingStatus, Trek, TrekStatus, TrekkerProfile, UserRole
from ..services.auth import role_required
from ..services.bookings import BookingError, cancel_booking, create_booking
from ..services.cache import Cache
from ..services.treks import search_treks
from ..services.common import app_now
from ..services.notifications import send_notification
from ..models import ExportJob
from .. import tasks
from .auth import fail, ok

bp = Blueprint("trekker", __name__)


def cache():
    return Cache(current_app.config["REDIS_URL"])


@bp.get("/dashboard")
@role_required(UserRole.TREKKER)
def dashboard():
    upcoming = Booking.query.filter_by(user_id=g.current_user.id, status=BookingStatus.BOOKED).all()
    available = cache().get("treks:public")
    if available is None:
        available = [trek.to_dict(include_staff=True) for trek in search_treks({"status": "APPROVED,OPEN"})]
    return ok({
        "available_treks": available,
        "booked_treks": [booking.to_dict() for booking in upcoming],
        "history_count": Booking.query.filter_by(user_id=g.current_user.id).count(),
    })


@bp.get("/bookings")
@role_required(UserRole.TREKKER)
def bookings():
    return ok([booking.to_dict() for booking in Booking.query.filter_by(user_id=g.current_user.id).order_by(Booking.booking_date.desc()).all()])


@bp.get("/history")
@role_required(UserRole.TREKKER)
def history():
    return ok([booking.to_dict() for booking in Booking.query.filter_by(user_id=g.current_user.id).order_by(Booking.booking_date.desc()).all()])


@bp.post("/treks/<int:trek_id>/book")
@role_required(UserRole.TREKKER)
def book(trek_id):
    try:
        booking = create_booking(g.current_user, trek_id)
    except BookingError as exc:
        return fail("BOOKING_ERROR", str(exc), 409)
    trek = booking.trek
    send_notification(current_app, g.current_user.email, "Trek booking confirmed", f"Your booking for {trek.name} is confirmed for {trek.start_date.isoformat()}.")
    cache().delete(f"trek:{trek.id}")
    cache().delete("treks:public")
    return ok(booking.to_dict(), 201)


@bp.post("/bookings/<int:booking_id>/cancel")
@role_required(UserRole.TREKKER)
def cancel(booking_id):
    try:
        booking = cancel_booking(g.current_user, booking_id)
    except BookingError as exc:
        return fail("CANCELLATION_ERROR", str(exc), 409)
    send_notification(current_app, g.current_user.email, "Trek booking cancelled", f"Your booking for {booking.trek.name} has been cancelled.")
    cache().delete(f"trek:{booking.trek_id}")
    cache().delete("treks:public")
    return ok(booking.to_dict())


@bp.patch("/profile")
@role_required(UserRole.TREKKER)
def update_profile():
    data = request.get_json(silent=True) or {}
    if "name" in data:
        g.current_user.name = str(data["name"]).strip()
    profile = g.current_user.student_profile
    if not profile:
        profile = TrekkerProfile(user_id=g.current_user.id)
        db.session.add(profile)
    profile.phone = str(data.get("phone", profile.phone or ""))
    profile.emergency_contact = str(data.get("emergency_contact", profile.emergency_contact or ""))
    db.session.commit()
    return ok(g.current_user.to_dict())


@bp.get("/profile")
@role_required(UserRole.TREKKER)
def get_profile():
    profile = g.current_user.student_profile
    return ok({**g.current_user.to_dict(), "profile": {"phone": profile.phone, "emergency_contact": profile.emergency_contact} if profile else {}})


@bp.post("/exports")
@role_required(UserRole.TREKKER)
def export_history():
    job = ExportJob(user_id=g.current_user.id, status="PENDING")
    db.session.add(job)
    db.session.commit()
    if tasks.celery:
        tasks.export_booking_history.delay(job.id)
    else:
        job.status = "PENDING"
        db.session.commit()
    return ok({"id": job.id, "status": job.status}, 202)


@bp.get("/exports/<int:job_id>")
@role_required(UserRole.TREKKER)
def export_status(job_id):
    job = db.session.get(ExportJob, job_id)
    if not job or job.user_id != g.current_user.id:
        return fail("NOT_FOUND", "Export job not found", 404)
    if job.status == "COMPLETED":
        return ok({"id": job.id, "status": job.status, "file": f"/api/v1/trekker/exports/{job.id}/download"})
    return ok({"id": job.id, "status": job.status, "error": job.error})


@bp.get("/exports/<int:job_id>/download")
@role_required(UserRole.TREKKER)
def download_export(job_id):
    job = db.session.get(ExportJob, job_id)
    if not job or job.user_id != g.current_user.id or job.status != "COMPLETED":
        return fail("NOT_FOUND", "Export file not available", 404)
    return send_file(job.file_path, as_attachment=True, download_name=f"trekking-history-{job.id}.csv")
