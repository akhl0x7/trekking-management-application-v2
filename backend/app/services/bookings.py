from sqlalchemy import update

from ..extensions import db
from ..models import Booking, BookingStatus, Trek, TrekStatus, UserStatus
from .common import app_now


class BookingError(Exception):
    pass


def create_booking(user, trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        raise BookingError("Trek not found")
    if user.status != UserStatus.ACTIVE:
        raise BookingError("User is not active")
    if trek.status != TrekStatus.OPEN:
        raise BookingError("Bookings are available only for open treks")
    if trek.start_date < app_now().date():
        raise BookingError("Trek has already started")
    existing = Booking.query.filter_by(user_id=user.id, trek_id=trek.id, status=BookingStatus.BOOKED).first()
    if existing:
        raise BookingError("User already has an active booking for this trek")
    result = db.session.execute(
        update(Trek)
        .where(Trek.id == trek.id, Trek.status == TrekStatus.OPEN, Trek.available_slots > 0)
        .values(available_slots=Trek.available_slots - 1)
    )
    if result.rowcount != 1:
        db.session.rollback()
        raise BookingError("No booking capacity remains")
    booking = Booking(
        user_id=user.id,
        trek_id=trek.id,
        booking_date=app_now(),
        status=BookingStatus.BOOKED,
    )
    db.session.add(booking)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise BookingError("Booking could not be completed") from exc
    return booking


def cancel_booking(user, booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        raise BookingError("Booking not found")
    if booking.user_id != user.id:
        raise BookingError("Booking does not belong to user")
    if booking.status != BookingStatus.BOOKED:
        raise BookingError("Only active bookings can be cancelled")
    if booking.trek.start_date < app_now().date():
        raise BookingError("Booking cannot be cancelled after trek start")
    booking.status = BookingStatus.CANCELLED
    db.session.execute(
        update(Trek).where(Trek.id == booking.trek_id).values(available_slots=Trek.available_slots + 1)
    )
    db.session.commit()
    return booking
