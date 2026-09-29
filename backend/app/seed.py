from datetime import timedelta
from decimal import Decimal

from .extensions import db
from .models import Difficulty, StaffProfile, Trek, TrekkerProfile, TrekStatus, TrekStaffAssignment, User, UserRole, UserStatus
from .services.common import app_now


def seed(app):
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email=app.config["ADMIN_EMAIL"]).first()
        if not admin:
            admin = User(email=app.config["ADMIN_EMAIL"], name="System Admin", role=UserRole.ADMIN, status=UserStatus.ACTIVE)
            admin.set_password(app.config["ADMIN_PASSWORD"])
            db.session.add(admin)

        staff_user = User.query.filter_by(email="staff@example.com").first()
        if not staff_user:
            staff_user = User(email="staff@example.com", name="Aarav Mehta", role=UserRole.STAFF, status=UserStatus.ACTIVE)
            staff_user.set_password("Staff@12345")
            db.session.add(staff_user)
            db.session.flush()
            staff_profile = StaffProfile(user_id=staff_user.id, employee_id="STAFF-1001", phone="9000000001", department="Operations")
            db.session.add(staff_profile)
        else:
            staff_profile = staff_user.staff_profile

        trekker = User.query.filter_by(email="trekker@example.com").first()
        if not trekker:
            trekker = User(email="trekker@example.com", name="Demo Trekker", role=UserRole.TREKKER, status=UserStatus.ACTIVE)
            trekker.set_password("Trekker@12345")
            db.session.add(trekker)
            db.session.flush()
            db.session.add(TrekkerProfile(user_id=trekker.id, phone="9000000002", emergency_contact="Demo Contact"))

        if not Trek.query.filter_by(name="Kalsubai Sunrise Trail").first():
            now = app_now().date()
            trek = Trek(
                name="Kalsubai Sunrise Trail",
                location="Maharashtra",
                difficulty=Difficulty.MODERATE,
                duration_days=1,
                capacity=12,
                available_slots=12,
                status=TrekStatus.OPEN,
                start_date=now + timedelta(days=5),
                end_date=now + timedelta(days=5),
                description="A one-day sunrise trek through the Sahyadri range.",
                instructions="Carry water, a rain layer and a headlamp.",
                price=Decimal("799.00"),
            )
            db.session.add(trek)
            db.session.flush()
            db.session.add(TrekStaffAssignment(trek_id=trek.id, staff_id=staff_profile.id))

        if not Trek.query.filter_by(name="Rajgad Ridge Walk").first():
            now = app_now().date()
            trek = Trek(
                name="Rajgad Ridge Walk",
                location="Pune",
                difficulty=Difficulty.EASY,
                duration_days=1,
                capacity=20,
                available_slots=20,
                status=TrekStatus.APPROVED,
                start_date=now + timedelta(days=10),
                end_date=now + timedelta(days=10),
                description="A guided fort and ridge walk.",
                instructions="Wear trekking shoes and carry personal medication.",
                price=Decimal("499.00"),
            )
            db.session.add(trek)
            db.session.flush()
            db.session.add(TrekStaffAssignment(trek_id=trek.id, staff_id=staff_profile.id))

        db.session.commit()
