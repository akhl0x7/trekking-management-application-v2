from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import or_

from ..extensions import db
from ..models import AssignmentStatus, Booking, Difficulty, StaffProfile, Trek, TrekStaffAssignment, TrekStatus, User, UserRole, UserStatus
from ..services.auth import role_required
from ..services.cache import Cache
from ..services.reports import monthly_report
from ..services.treks import TrekError, invalidate_trek_cache, transition_trek, validate_trek_payload
from .auth import fail, ok

bp = Blueprint("admin", __name__)


def cache():
    return Cache(current_app.config["REDIS_URL"])


@bp.get("/dashboard")
@role_required(UserRole.ADMIN)
def dashboard():
    return ok({
        "treks": Trek.query.count(),
        "users": User.query.filter_by(role=UserRole.TREKKER).count(),
        "staff": User.query.filter_by(role=UserRole.STAFF).count(),
        "bookings": Booking.query.count(),
        "open_treks": Trek.query.filter_by(status=TrekStatus.OPEN).count(),
    })


@bp.get("/treks")
@role_required(UserRole.ADMIN)
def list_treks():
    search = request.args.get("search", "").strip()
    query = Trek.query
    if search:
        query = query.filter(or_(Trek.name.ilike(f"%{search}%"), Trek.location.ilike(f"%{search}%")))
    return ok([trek.to_dict(include_staff=True) for trek in query.order_by(Trek.id.desc()).all()])


@bp.post("/treks")
@role_required(UserRole.ADMIN)
def create_trek():
    try:
        values = validate_trek_payload(request.get_json(silent=True) or {})
    except TrekError as exc:
        return fail("VALIDATION_ERROR", str(exc), 400)
    trek = Trek(**values, status=TrekStatus.PENDING)
    db.session.add(trek)
    db.session.commit()
    return ok(trek.to_dict(include_staff=True), 201)


@bp.get("/treks/<int:trek_id>")
@role_required(UserRole.ADMIN)
def get_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return fail("NOT_FOUND", "Trek not found", 404)
    return ok(trek.to_dict(include_staff=True))


@bp.patch("/treks/<int:trek_id>")
@role_required(UserRole.ADMIN)
def update_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return fail("NOT_FOUND", "Trek not found", 404)
    try:
        values = validate_trek_payload(request.get_json(silent=True) or {}, trek)
    except TrekError as exc:
        return fail("VALIDATION_ERROR", str(exc), 400)
    payload = request.get_json(silent=True) or {}
    active = sum(1 for b in trek.bookings if b.status.value == "BOOKED")
    if "capacity" in payload and "available_slots" not in payload:
        values["available_slots"] = values["capacity"] - active
    if values["available_slots"] > values["capacity"]:
        return fail("CAPACITY_INVALID", "Available slots cannot exceed capacity", 409)
    for key, value in values.items():
        setattr(trek, key, value)
    db.session.commit()
    invalidate_trek_cache(cache(), trek.id)
    return ok(trek.to_dict(include_staff=True))


@bp.delete("/treks/<int:trek_id>")
@role_required(UserRole.ADMIN)
def delete_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return fail("NOT_FOUND", "Trek not found", 404)
    if trek.bookings:
        return fail("HAS_HISTORY", "Trek with booking history cannot be deleted", 409)
    db.session.delete(trek)
    db.session.commit()
    invalidate_trek_cache(cache(), trek.id)
    return ok({"deleted": True})


@bp.post("/treks/<int:trek_id>/approve")
@role_required(UserRole.ADMIN)
def approve_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return fail("NOT_FOUND", "Trek not found", 404)
    try:
        transition_trek(trek, TrekStatus.APPROVED, "ADMIN")
    except TrekError as exc:
        return fail("INVALID_TRANSITION", str(exc), 409)
    db.session.commit()
    invalidate_trek_cache(cache(), trek.id)
    return ok(trek.to_dict(include_staff=True))


@bp.get("/staff")
@role_required(UserRole.ADMIN)
def list_staff():
    search = request.args.get("search", "").strip()
    query = User.query.filter_by(role=UserRole.STAFF)
    if search:
        query = query.filter(or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")))
    result = []
    for user in query.order_by(User.id.desc()).all():
        result.append({**user.to_dict(), "staff_profile": {"id": user.staff_profile.id, "employee_id": user.staff_profile.employee_id, "phone": user.staff_profile.phone, "department": user.staff_profile.department} if user.staff_profile else None})
    return ok(result)


@bp.post("/staff")
@role_required(UserRole.ADMIN)
def create_staff():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    name = str(data.get("name", "")).strip()
    employee_id = str(data.get("employee_id", "")).strip()
    if not all([email, password, name, employee_id]):
        return fail("VALIDATION_ERROR", "email, password, name and employee_id are required", 400)
    if User.query.filter_by(email=email).first() or StaffProfile.query.filter_by(employee_id=employee_id).first():
        return fail("DUPLICATE", "Staff account or employee ID already exists", 409)
    user = User(email=email, name=name, role=UserRole.STAFF, status=UserStatus.ACTIVE)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    profile = StaffProfile(user_id=user.id, employee_id=employee_id, phone=data.get("phone", ""), department=data.get("department", ""))
    db.session.add(profile)
    db.session.commit()
    return ok({**user.to_dict(), "staff_profile": {"id": profile.id, "employee_id": profile.employee_id, "phone": profile.phone, "department": profile.department}}, 201)


@bp.patch("/staff/<int:user_id>/status")
@role_required(UserRole.ADMIN)
def update_staff_status(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != UserRole.STAFF:
        return fail("NOT_FOUND", "Staff member not found", 404)
    status = str((request.get_json(silent=True) or {}).get("status", "")).upper()
    try:
        user.status = UserStatus(status)
    except ValueError:
        return fail("VALIDATION_ERROR", "Invalid user status", 400)
    db.session.commit()
    return ok(user.to_dict())


@bp.post("/treks/<int:trek_id>/assign")
@role_required(UserRole.ADMIN)
def assign_staff(trek_id):
    trek = db.session.get(Trek, trek_id)
    staff_id = (request.get_json(silent=True) or {}).get("staff_id")
    staff = db.session.get(StaffProfile, staff_id) if staff_id else None
    if not trek or not staff or staff.user.status != UserStatus.ACTIVE:
        return fail("INVALID_ASSIGNMENT", "Trek or active staff member not found", 400)
    assignment = TrekStaffAssignment.query.filter_by(trek_id=trek.id, staff_id=staff.id).first()
    if assignment:
        assignment.status = AssignmentStatus.ACTIVE
        assignment.unassigned_at = None
    else:
        assignment = TrekStaffAssignment(trek_id=trek.id, staff_id=staff.id, status=AssignmentStatus.ACTIVE)
        db.session.add(assignment)
    db.session.commit()
    invalidate_trek_cache(cache(), trek.id)
    return ok(trek.to_dict(include_staff=True))


@bp.post("/treks/<int:trek_id>/unassign")
@role_required(UserRole.ADMIN)
def unassign_staff(trek_id):
    data = request.get_json(silent=True) or {}
    assignment = TrekStaffAssignment.query.filter_by(trek_id=trek_id, staff_id=data.get("staff_id")).first()
    if not assignment:
        return fail("NOT_FOUND", "Assignment not found", 404)
    assignment.status = AssignmentStatus.INACTIVE
    assignment.unassigned_at = __import__("datetime").datetime.utcnow()
    db.session.commit()
    invalidate_trek_cache(cache(), trek_id)
    return ok({"unassigned": True})


@bp.get("/users")
@role_required(UserRole.ADMIN)
def users():
    search = request.args.get("search", "").strip()
    query = User.query.filter_by(role=UserRole.TREKKER)
    if search:
        query = query.filter(or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")))
    return ok([u.to_dict() for u in query.order_by(User.id.desc()).all()])


@bp.patch("/users/<int:user_id>/status")
@role_required(UserRole.ADMIN)
def update_user_status(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != UserRole.TREKKER:
        return fail("NOT_FOUND", "User not found", 404)
    status = str((request.get_json(silent=True) or {}).get("status", "")).upper()
    try:
        user.status = UserStatus(status)
    except ValueError:
        return fail("VALIDATION_ERROR", "Invalid user status", 400)
    db.session.commit()
    return ok(user.to_dict())


@bp.get("/bookings")
@role_required(UserRole.ADMIN)
def bookings():
    return ok([booking.to_dict() for booking in Booking.query.order_by(Booking.booking_date.desc()).all()])


@bp.get("/reports")
@role_required(UserRole.ADMIN)
def reports():
    return ok(monthly_report())
