from flask import Blueprint, jsonify, request, current_app

from ..extensions import db
from ..models import AssignmentStatus, Booking, BookingStatus, StaffProfile, Trek, TrekStaffAssignment, TrekStatus, UserRole
from ..services.auth import role_required
from ..services.cache import Cache
from ..services.treks import TrekError, invalidate_trek_cache, transition_trek
from .auth import fail, ok

bp = Blueprint("staff", __name__)


def cache():
    return Cache(current_app.config["REDIS_URL"])


def assigned_trek(staff_profile_id, trek_id):
    assignment = TrekStaffAssignment.query.filter_by(trek_id=trek_id, staff_id=staff_profile_id, status=AssignmentStatus.ACTIVE).first()
    if not assignment:
        return None
    return db.session.get(Trek, trek_id)


@bp.get("/dashboard")
@role_required(UserRole.STAFF)
def dashboard():
    from flask import g
    profile = g.current_user.staff_profile
    assignments = TrekStaffAssignment.query.filter_by(staff_id=profile.id, status=AssignmentStatus.ACTIVE).all()
    return ok({
        "assigned_treks": len(assignments),
        "treks": [assignment.trek.to_dict(include_staff=True) for assignment in assignments],
        "registered_users": sum(Booking.query.filter_by(trek_id=assignment.trek_id, status=BookingStatus.BOOKED).count() for assignment in assignments),
    })


@bp.get("/treks")
@role_required(UserRole.STAFF)
def treks():
    from flask import g
    profile = g.current_user.staff_profile
    assignments = TrekStaffAssignment.query.filter_by(staff_id=profile.id, status=AssignmentStatus.ACTIVE).all()
    return ok([assignment.trek.to_dict(include_staff=True) for assignment in assignments])


@bp.get("/treks/<int:trek_id>/participants")
@role_required(UserRole.STAFF)
def participants(trek_id):
    from flask import g
    trek = assigned_trek(g.current_user.staff_profile.id, trek_id)
    if not trek:
        return fail("FORBIDDEN", "Staff is not assigned to this trek", 403)
    return ok([booking.to_dict() for booking in trek.bookings])


@bp.patch("/treks/<int:trek_id>")
@role_required(UserRole.STAFF)
def update_trek(trek_id):
    from flask import g
    trek = assigned_trek(g.current_user.staff_profile.id, trek_id)
    if not trek:
        return fail("FORBIDDEN", "Staff is not assigned to this trek", 403)
    data = request.get_json(silent=True) or {}
    if "available_slots" in data:
        try:
            available_slots = int(data["available_slots"])
        except (TypeError, ValueError):
            return fail("VALIDATION_ERROR", "available_slots must be an integer", 400)
        if available_slots < 0 or available_slots > trek.capacity:
            return fail("VALIDATION_ERROR", "available_slots must be between 0 and capacity", 400)
        trek.available_slots = available_slots
    if "capacity" in data:
        try:
            capacity = int(data["capacity"])
        except (TypeError, ValueError):
            return fail("VALIDATION_ERROR", "capacity must be an integer", 400)
        active = Booking.query.filter_by(trek_id=trek.id, status=BookingStatus.BOOKED).count()
        if capacity <= 0 or capacity < active:
            return fail("CAPACITY_TOO_LOW", "Capacity cannot be below active bookings", 409)
        trek.capacity = capacity
        trek.available_slots = max(0, capacity - active)
    if "status" in data:
        try:
            transition_trek(trek, TrekStatus(data["status"]), "STAFF")
        except (ValueError, TrekError) as exc:
            return fail("INVALID_TRANSITION", str(exc), 409)
    db.session.commit()
    invalidate_trek_cache(cache(), trek.id)
    return ok(trek.to_dict(include_staff=True))


@bp.post("/treks/<int:trek_id>/start")
@role_required(UserRole.STAFF)
def start_trek(trek_id):
    from flask import g
    trek = assigned_trek(g.current_user.staff_profile.id, trek_id)
    if not trek:
        return fail("FORBIDDEN", "Staff is not assigned to this trek", 403)
    if trek.status != TrekStatus.OPEN:
        return fail("INVALID_STATE", "Only open treks can be started", 409)
    trek.started_at = __import__("datetime").datetime.utcnow()
    trek.status = TrekStatus.CLOSED
    db.session.commit()
    invalidate_trek_cache(cache(), trek.id)
    return ok(trek.to_dict(include_staff=True))


@bp.post("/treks/<int:trek_id>/complete")
@role_required(UserRole.STAFF)
def complete_trek(trek_id):
    from flask import g
    trek = assigned_trek(g.current_user.staff_profile.id, trek_id)
    if not trek:
        return fail("FORBIDDEN", "Staff is not assigned to this trek", 403)
    try:
        transition_trek(trek, TrekStatus.COMPLETED, "STAFF")
    except TrekError as exc:
        return fail("INVALID_TRANSITION", str(exc), 409)
    db.session.commit()
    invalidate_trek_cache(cache(), trek.id)
    return ok(trek.to_dict(include_staff=True))
