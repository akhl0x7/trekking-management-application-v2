import tempfile
from pathlib import Path

import pytest

from app import create_app
from app.extensions import db
from app.models import StaffProfile, Trek, TrekkerProfile, User, UserRole, UserStatus, Difficulty, TrekStatus, TrekStaffAssignment


@pytest.fixture()
def app():
    with tempfile.TemporaryDirectory() as temp:
        db_path = Path(temp) / "test.db"
        app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "ADMIN_EMAIL": "admin@test.local",
            "ADMIN_PASSWORD": "Admin@12345",
            "REDIS_URL": "redis://127.0.0.1:6399/0",
            "CELERY_BROKER_URL": "redis://127.0.0.1:6399/0",
            "CELERY_RESULT_BACKEND": "redis://127.0.0.1:6399/0",
            "CELERY_TASK_ALWAYS_EAGER": True,
        })
        with app.app_context():
            db.create_all()
            admin = User(email="admin@test.local", name="Admin", role=UserRole.ADMIN, status=UserStatus.ACTIVE)
            admin.set_password("Admin@12345")
            staff = User(email="staff@test.local", name="Staff", role=UserRole.STAFF, status=UserStatus.ACTIVE)
            staff.set_password("Staff@12345")
            student = User(email="student@test.local", name="Student", role=UserRole.TREKKER, status=UserStatus.ACTIVE)
            student.set_password("Student@12345")
            db.session.add_all([admin, staff, student])
            db.session.flush()
            staff_profile = StaffProfile(user_id=staff.id, employee_id="S1", department="Ops")
            student_profile = TrekkerProfile(user_id=student.id)
            db.session.add_all([staff_profile, student_profile])
            db.session.flush()
            from datetime import timedelta
            from app.services.common import app_now
            today = app_now().date()
            trek = Trek(name="Test Trek", location="Pune", difficulty=Difficulty.EASY, duration_days=1, capacity=1, available_slots=1, status=TrekStatus.OPEN, start_date=today + timedelta(days=2), end_date=today + timedelta(days=2), price=100)
            db.session.add(trek)
            db.session.flush()
            db.session.add(TrekStaffAssignment(trek_id=trek.id, staff_id=staff_profile.id))
            db.session.commit()
        yield app
        with app.app_context():
            db.session.remove()
            db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
