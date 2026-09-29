def login_student(client):
    client.post("/api/v1/auth/login", json={"email": "student@test.local", "password": "Student@12345"})


def test_booking_consumes_one_slot(client):
    login_student(client)
    response = client.post("/api/v1/trekker/treks/1/book")
    assert response.status_code == 201
    assert response.json["data"]["status"] == "BOOKED"
    trek = client.get("/api/v1/treks/1").json["data"]
    assert trek["available_slots"] == 0


def test_cancellation_restores_slot(client):
    login_student(client)
    booking = client.post("/api/v1/trekker/treks/1/book").json["data"]
    assert client.get("/api/v1/treks/1").json["data"]["available_slots"] == 0
    assert client.post(f"/api/v1/trekker/bookings/{booking["id"]}/cancel").status_code == 200
    assert client.get("/api/v1/treks/1").json["data"]["available_slots"] == 1


def test_duplicate_booking_is_rejected(client):
    login_student(client)
    assert client.post("/api/v1/trekker/treks/1/book").status_code == 201
    response = client.post("/api/v1/trekker/treks/1/book")
    assert response.status_code == 409


def test_full_trek_rejects_second_user(client, app):
    login_student(client)
    assert client.post("/api/v1/trekker/treks/1/book").status_code == 201
    with app.app_context():
        from app.models import User, TrekkerProfile, UserRole, UserStatus
        from app.extensions import db
        user = User(email="other@test.local", name="Other", role=UserRole.TREKKER, status=UserStatus.ACTIVE)
        user.set_password("Other@12345")
        db.session.add(user)
        db.session.flush()
        db.session.add(TrekkerProfile(user_id=user.id))
        db.session.commit()
    client.post("/api/v1/auth/logout")
    client.post("/api/v1/auth/login", json={"email": "other@test.local", "password": "Other@12345"})
    response = client.post("/api/v1/trekker/treks/1/book")
    assert response.status_code == 409
