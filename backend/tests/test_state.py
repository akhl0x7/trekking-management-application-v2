from app.models import TrekStatus


def test_staff_can_start_and_complete_open_trek(client):
    client.post("/api/v1/auth/login", json={"email": "staff@test.local", "password": "Staff@12345"})
    response = client.post("/api/v1/staff/treks/1/start")
    assert response.status_code == 200
    assert response.json["data"]["status"] == "CLOSED"
    response = client.post("/api/v1/staff/treks/1/complete")
    assert response.status_code == 200
    assert response.json["data"]["status"] == "COMPLETED"


def test_invalid_status_transition_is_rejected(client):
    client.post("/api/v1/auth/login", json={"email": "staff@test.local", "password": "Staff@12345"})
    response = client.patch("/api/v1/staff/treks/1", json={"status": TrekStatus.APPROVED.value})
    assert response.status_code == 409
