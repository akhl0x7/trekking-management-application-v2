from functools import wraps

from flask import g, session

from ..models import User, UserRole, UserStatus


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = User.query.get(user_id)
    if not user or user.status != UserStatus.ACTIVE:
        session.clear()
        return None
    return user


def require_auth():
    user = current_user()
    if not user:
        raise PermissionError("Authentication required")
    g.current_user = user
    return user


def role_required(*roles):
    allowed = {role.value if isinstance(role, UserRole) else role for role in roles}

    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user = require_auth()
            if user.role.value not in allowed:
                raise PermissionError("Insufficient permissions")
            return fn(*args, **kwargs)

        return wrapped

    return decorator
