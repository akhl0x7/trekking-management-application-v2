def test_login_and_me(client):
    response = client.post("/api/v1/auth/login", json={"email": "student@test.local", "password": "Student@12345"})
    assert response.status_code == 200
    assert response.json["data"]["role"] == "TREKKER"
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json["data"]["email"] == "student@test.local"


def test_staff_and_admin_registration_are_blocked(client):
    response = client.post("/api/v1/auth/register", json={"name": "X", "email": "x@test.local", "password": "Password123"})
    assert response.status_code == 201
    assert response.json["data"]["role"] == "TREKKER"
