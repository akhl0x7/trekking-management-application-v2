import enum
import hashlib
import secrets
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Index, UniqueConstraint

from .extensions import db


class UserRole(enum.StrEnum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    TREKKER = "TREKKER"


class UserStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLACKLISTED = "BLACKLISTED"


class Difficulty(enum.StrEnum):
    EASY = "EASY"
    MODERATE = "MODERATE"
    HARD = "HARD"


class TrekStatus(enum.StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    COMPLETED = "COMPLETED"


class AssignmentStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class BookingStatus(enum.StrEnum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class PaymentStatus(enum.StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, index=True)
    status = db.Column(db.Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    student_profile = db.relationship(
        "TrekkerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    staff_profile = db.relationship(
        "StaffProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    bookings = db.relationship("Booking", back_populates="user")

    def set_password(self, password):
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64
        )
        self.password_hash = f"scrypt${salt.hex()}${digest.hex()}"

    def check_password(self, password):
        try:
            _, salt_hex, digest_hex = self.password_hash.split("$", 2)
        except ValueError:
            return False
        salt = bytes.fromhex(salt_hex)
        digest = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64
        )
        return secrets.compare_digest(digest.hex(), digest_hex)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role.value,
            "status": self.status.value,
        }


class TrekkerProfile(db.Model):
    __tablename__ = "trekker_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    phone = db.Column(db.String(40), default="")
    emergency_contact = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="student_profile")


class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    employee_id = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(40), default="")
    department = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="staff_profile")


class Trek(db.Model):
    __tablename__ = "treks"
    __table_args__ = (
        CheckConstraint("duration_days > 0", name="ck_trek_duration_positive"),
        CheckConstraint("capacity > 0", name="ck_trek_capacity_positive"),
        CheckConstraint("available_slots >= 0", name="ck_trek_capacity_nonnegative"),
        CheckConstraint("available_slots <= capacity", name="ck_trek_available_lte_capacity"),
        CheckConstraint("start_date <= end_date", name="ck_trek_dates_order"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    location = db.Column(db.String(160), nullable=False, index=True)
    difficulty = db.Column(db.Enum(Difficulty), nullable=False, index=True)
    duration_days = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(TrekStatus), nullable=False, default=TrekStatus.PENDING, index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, default="")
    instructions = db.Column(db.Text, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignments = db.relationship(
        "TrekStaffAssignment", back_populates="trek", cascade="all, delete-orphan"
    )
    bookings = db.relationship("Booking", back_populates="trek", cascade="all, delete-orphan")

    def to_dict(self, include_staff=False):
        data = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "difficulty": self.difficulty.value,
            "duration_days": self.duration_days,
            "capacity": self.capacity,
            "available_slots": self.available_slots,
            "status": self.status.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "description": self.description,
            "instructions": self.instructions,
            "price": float(self.price),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        if include_staff:
            data["staff"] = [
                {
                    "assignment_id": a.id,
                    "staff_id": a.staff_id,
                    "name": a.staff.user.name,
                    "employee_id": a.staff.employee_id,
                    "status": a.status.value,
                }
                for a in self.assignments
                if a.status == AssignmentStatus.ACTIVE
            ]
        return data


class TrekStaffAssignment(db.Model):
    __tablename__ = "trek_staff_assignments"
    __table_args__ = (UniqueConstraint("trek_id", "staff_id", name="uq_trek_staff"),)

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id", ondelete="CASCADE"), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff_profiles.id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.Enum(AssignmentStatus), nullable=False, default=AssignmentStatus.ACTIVE)
    assigned_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    unassigned_at = db.Column(db.DateTime, nullable=True)

    trek = db.relationship("Trek", back_populates="assignments")
    staff = db.relationship("StaffProfile")


class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("status IN ('BOOKED', 'CANCELLED', 'COMPLETED')", name="ck_booking_status"),
        Index(
            "uq_active_booking_user_trek",
            "user_id",
            "trek_id",
            unique=True,
            sqlite_where=db.text("status = 'BOOKED'"),
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id", ondelete="RESTRICT"), nullable=False, index=True)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum(BookingStatus), nullable=False, default=BookingStatus.BOOKED, index=True)
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.NOT_REQUIRED)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_email": self.user.email,
            "trek_id": self.trek_id,
            "trek_name": self.trek.name,
            "location": self.trek.location,
            "booking_date": self.booking_date.isoformat(),
            "status": self.status.value,
            "payment_status": self.payment_status.value,
            "start_date": self.trek.start_date.isoformat(),
            "end_date": self.trek.end_date.isoformat(),
        }


class ExportJob(db.Model):
    __tablename__ = "export_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="PENDING", index=True)
    file_path = db.Column(db.String(500), default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    error = db.Column(db.Text, default="")
    user = db.relationship("User")
