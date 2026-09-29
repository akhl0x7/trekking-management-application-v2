import pytest
from sqlalchemy.exc import IntegrityError


def test_trek_capacity_constraint(app):
    from app.extensions import db
    from app.models import Trek, Difficulty, TrekStatus
    from datetime import date, timedelta
    with app.app_context():
        trek = Trek(name="Bad", location="X", difficulty=Difficulty.EASY, duration_days=1, capacity=1, available_slots=2, status=TrekStatus.OPEN, start_date=date.today()+timedelta(days=2), end_date=date.today()+timedelta(days=2))
        db.session.add(trek)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
