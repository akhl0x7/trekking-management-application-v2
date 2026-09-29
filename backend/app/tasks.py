import csv
from datetime import timedelta
from pathlib import Path

from .celery_app import create_celery
from .extensions import db
from .models import Booking, BookingStatus, ExportJob, Trek, User
from .services.common import app_now
from .services.notifications import send_notification
from .services.reports import monthly_report, render_report

celery = None
send_daily_reminders = None
generate_monthly_report = None
export_booking_history = None


def init_tasks(app):
    global celery, send_daily_reminders, generate_monthly_report, export_booking_history
    celery = create_celery(app)

    @celery.task(name="app.tasks.send_daily_reminders")
    def _send_daily_reminders():
        tomorrow = app_now().date() + timedelta(days=1)
        bookings = (
            db.session.query(Booking)
            .join(Trek)
            .join(User)
            .filter(Booking.status == BookingStatus.BOOKED, Trek.start_date == tomorrow)
            .all()
        )
        count = 0
        for booking in bookings:
            trek = booking.trek
            send_notification(
                app,
                booking.user.email,
                f"Upcoming trek: {trek.name}",
                f"Your trek {trek.name} starts on {trek.start_date.isoformat()}. {trek.instructions}",
            )
            count += 1
        return {"sent": count}

    @celery.task(name="app.tasks.generate_monthly_report")
    def _generate_monthly_report():
        data = monthly_report()
        html = render_report(data)
        path = Path(app.instance_path) / "reports" / f"report-{app_now().strftime('%Y-%m')}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        send_notification(
            app,
            app.config["ADMIN_EMAIL"],
            "Monthly Trekking Activity Report",
            f"Report generated at {path}",
        )
        return {"path": str(path), **data}

    @celery.task(name="app.tasks.export_booking_history")
    def _export_booking_history(export_job_id):
        job = db.session.get(ExportJob, export_job_id)
        if not job:
            return {"status": "NOT_FOUND"}
        try:
            bookings = Booking.query.filter_by(user_id=job.user_id).order_by(Booking.booking_date.asc()).all()
            path = Path(app.instance_path) / "exports" / f"booking-history-{job.id}.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["User ID", "Trek Name", "Location", "Booking Status", "Start Date", "End Date"])
                for booking in bookings:
                    writer.writerow([
                        booking.user_id,
                        booking.trek.name,
                        booking.trek.location,
                        booking.status.value,
                        booking.trek.start_date.isoformat(),
                        booking.trek.end_date.isoformat(),
                    ])
            job.status = "COMPLETED"
            job.file_path = str(path)
            job.completed_at = app_now()
            db.session.commit()
            user = db.session.get(User, job.user_id)
            send_notification(
                app,
                user.email,
                "Trekking history export completed",
                f"Your export is ready at {path.name}.",
            )
            return {"status": "COMPLETED", "path": str(path)}
        except Exception as exc:
            job.status = "FAILED"
            job.error = str(exc)
            db.session.commit()
            raise

    send_daily_reminders = _send_daily_reminders
    generate_monthly_report = _generate_monthly_report
    export_booking_history = _export_booking_history
    return celery
