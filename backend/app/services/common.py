from datetime import datetime, timezone


def app_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def serialize(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value
