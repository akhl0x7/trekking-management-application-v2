from calendar import monthrange
from datetime import date

from sqlalchemy import and_, func

from ..extensions import db
from ..models import Booking, BookingStatus, Trek, TrekStatus


def previous_month_range(today):
    first_this_month = today.replace(day=1)
    previous_month_end = first_this_month.fromordinal(first_this_month.toordinal() - 1)
    previous_month_start = previous_month_end.replace(day=1)
    return previous_month_start, previous_month_end


def monthly_report(today=None):
    today = today or date.today()
    start, end = previous_month_range(today)
    conducted = (
        db.session.query(func.count(Trek.id))
        .filter(Trek.status == TrekStatus.COMPLETED, Trek.end_date.between(start, end))
        .scalar()
        or 0
    )
    participants = (
        db.session.query(func.count(func.distinct(Booking.user_id)))
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(Booking.status == BookingStatus.COMPLETED, Trek.end_date.between(start, end))
        .scalar()
        or 0
    )
    popular = (
        db.session.query(Trek.name, func.count(Booking.id).label("count"))
        .join(Booking, Booking.trek_id == Trek.id)
        .filter(
            Booking.status.in_([BookingStatus.BOOKED, BookingStatus.COMPLETED]),
            Trek.start_date.between(start, end),
        )
        .group_by(Trek.id)
        .order_by(func.count(Booking.id).desc(), Trek.name.asc())
        .limit(10)
        .all()
    )
    return {
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "treks_conducted": conducted,
        "users_participated": participants,
        "popular_treks": [{"name": name, "bookings": count} for name, count in popular],
    }


def render_report(data):
    rows = "".join(f"<tr><td>{item['name']}</td><td>{item['bookings']}</td></tr>" for item in data["popular_treks"])
    return f"""<!doctype html><html><body><h1>Monthly Trekking Activity Report</h1><p>Period: {data['period_start']} to {data['period_end']}</p><p>Treks conducted: {data['treks_conducted']}</p><p>Users participated: {data['users_participated']}</p><table border='1'><tr><th>Trek</th><th>Bookings</th></tr>{rows}</table></body></html>"""
