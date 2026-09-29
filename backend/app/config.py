from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import or_, select

from ..extensions import db
from ..models import AssignmentStatus, Difficulty, Trek, TrekStaffAssignment, TrekStatus, UserStatus
from .cache import Cache
from .common import app_now

ALLOWED_TRANSITIONS = {
    TrekStatus.PENDING: {TrekStatus.APPROVED},
    TrekStatus.APPROVED: {TrekStatus.OPEN},
    TrekStatus.OPEN: {TrekStatus.CLOSED},
    TrekStatus.CLOSED: {TrekStatus.COMPLETED, TrekStatus.OPEN},
    TrekStatus.COMPLETED: set(),
}


class TrekError(Exception):
    pass


def transition_trek(trek, target, actor_role):
    if target not in ALLOWED_TRANSITIONS[trek.status]:
        raise TrekError(f"Invalid transition from {trek.status.value} to {target.value}")
    if target == TrekStatus.OPEN and trek.started_at is not None:
        raise TrekError("A started trek cannot be reopened")
    if actor_role == "STAFF" and target not in {TrekStatus.OPEN, TrekStatus.CLOSED, TrekStatus.COMPLETED}:
        raise TrekError("Staff cannot perform this transition")
    if actor_role == "ADMIN" and target == TrekStatus.COMPLETED:
        raise TrekError("Staff must complete a trek")
    trek.status = target
    if target == TrekStatus.OPEN:
        trek.started_at = None
    if target == TrekStatus.CLOSED and trek.started_at is None:
        trek.started_at = app_now()
    if target == TrekStatus.COMPLETED:
        trek.completed_at = app_now()
        trek.status = TrekStatus.COMPLETED
        for booking in trek.bookings:
            if booking.status.value == "BOOKED":
                booking.status = "COMPLETED"
    return trek


def validate_trek_payload(data, existing=None):
    values = {
        "name": data.get("name", existing.name if existing else None),
        "location": data.get("location", existing.location if existing else None),
        "difficulty": data.get("difficulty", existing.difficulty.value if existing else None),
        "duration_days": data.get("duration_days", existing.duration_days if existing else None),
        "capacity": data.get("capacity", existing.capacity if existing else data.get("available_slots", None)),
        "available_slots": data.get("available_slots", existing.available_slots if existing else data.get("capacity", None)),
        "start_date": data.get("start_date", existing.start_date.isoformat() if existing else None),
        "end_date": data.get("end_date", existing.end_date.isoformat() if existing else None),
        "description": data.get("description", existing.description if existing else ""),
        "instructions": data.get("instructions", existing.instructions if existing else ""),
        "price": data.get("price", float(existing.price) if existing else 0),
    }
    if not values["name"] or not values["location"]:
        raise TrekError("name and location are required")
    try:
        difficulty = Difficulty(values["difficulty"])
    except ValueError as exc:
        raise TrekError("Invalid difficulty") from exc
    try:
        duration_days = int(values["duration_days"])
        capacity = int(values["capacity"])
        available_slots = int(values["available_slots"])
        price = Decimal(str(values["price"]))
    except (TypeError, ValueError, InvalidOperation) as exc:
        raise TrekError("Invalid numeric value") from exc
    try:
        start_date = date.fromisoformat(values["start_date"])
        end_date = date.fromisoformat(values["end_date"])
    except (TypeError, ValueError) as exc:
        raise TrekError("Invalid date") from exc
    if duration_days <= 0 or capacity <= 0 or available_slots < 0 or available_slots > capacity or price < 0:
        raise TrekError("Invalid trek values")
    if start_date > end_date:
        raise TrekError("start_date must be on or before end_date")
    values.update(
        difficulty=difficulty,
        duration_days=duration_days,
        capacity=capacity,
        available_slots=available_slots,
        price=price,
        start_date=start_date,
        end_date=end_date,
    )
    return values


def search_treks(args):
    stmt = select(Trek)
    status = args.get("status")
    difficulty = args.get("difficulty")
    location = args.get("location")
    search = args.get("search")
    duration = args.get("duration")
    if status:
        statuses = [item.strip() for item in status.split(",") if item.strip()]
        try:
            status_values = [TrekStatus(item) for item in statuses]
        except ValueError as exc:
            raise TrekError("Invalid status filter") from exc
        if len(status_values) == 1:
            stmt = stmt.where(Trek.status == status_values[0])
        else:
            stmt = stmt.where(Trek.status.in_(status_values))
    if difficulty:
        stmt = stmt.where(Trek.difficulty == Difficulty(difficulty))
    if location:
        stmt = stmt.where(Trek.location.ilike(f"%{location}%"))
    if search:
        stmt = stmt.where(or_(Trek.name.ilike(f"%{search}%"), Trek.location.ilike(f"%{search}%")))
    if duration:
        stmt = stmt.where(Trek.duration_days == int(duration))
    stmt = stmt.order_by(Trek.start_date.asc(), Trek.id.asc())
    return db.session.scalars(stmt).all()


def invalidate_trek_cache(cache, trek_id):
    cache.delete(f"trek:{trek_id}")
    cache.delete("treks:public")
