from celery import Celery
from celery.schedules import crontab


def create_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
    )
    celery.conf.update(
        timezone="UTC",
        task_track_started=True,
        task_always_eager=app.config.get("CELERY_TASK_ALWAYS_EAGER", False),
        beat_schedule={
            "daily-trek-reminders": {
                "task": "app.tasks.send_daily_reminders",
                "schedule": crontab(hour=8, minute=0),
            },
            "monthly-trek-report": {
                "task": "app.tasks.generate_monthly_report",
                "schedule": crontab(day_of_month=1, hour=8, minute=30),
            },
        },
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
