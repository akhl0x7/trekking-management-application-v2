def test_student_cannot_access_admin(client):
    client.post("/api/v1/auth/login", json={"email": "student@test.local", "password": "Student@12345"})
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 403


def test_staff_can_access_assigned_treks(client):
    client.post("/api/v1/auth/login", json={"email": "staff@test.local", "password": "Staff@12345"})
    response = client.get("/api/v1/staff/treks")
    assert response.status_code == 200
    assert len(response.json["data"]) == 1
