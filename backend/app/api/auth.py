from flask import Blueprint, jsonify, request, session

from ..extensions import db
from ..models import TrekkerProfile, User, UserRole, UserStatus
from ..services.auth import current_user

bp = Blueprint("auth", __name__)


def ok(data=None, status=200):
    return jsonify({"data": data, "error": None}), status


def fail(code, message, status):
    return jsonify({"data": None, "error": {"code": code, "message": message}}), status


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    name = str(data.get("name", "")).strip()
    if not email or not password or not name:
        return fail("VALIDATION_ERROR", "email, password and name are required", 400)
    if User.query.filter_by(email=email).first():
        return fail("EMAIL_EXISTS", "Email is already registered", 409)
    user = User(email=email, name=name, role=UserRole.TREKKER, status=UserStatus.ACTIVE)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    db.session.add(TrekkerProfile(user_id=user.id))
    db.session.commit()
    session["user_id"] = user.id
    return ok(user.to_dict(), 201)


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(email=str(data.get("email", "")).strip().lower()).first()
    if not user or not user.check_password(str(data.get("password", ""))):
        return fail("INVALID_CREDENTIALS", "Invalid email or password", 401)
    if user.status != UserStatus.ACTIVE:
        return fail("ACCOUNT_UNAVAILABLE", "Account is not active", 403)
    session.clear()
    session["user_id"] = user.id
    return ok(user.to_dict())


@bp.post("/logout")
def logout():
    session.clear()
    return ok({"logged_out": True})


@bp.get("/me")
def me():
    user = current_user()
    if not user:
        return fail("UNAUTHENTICATED", "Authentication required", 401)
    return ok(user.to_dict())
