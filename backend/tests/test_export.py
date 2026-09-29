def test_export_requires_ownership(client):
    client.post("/api/v1/auth/login", json={"email": "student@test.local", "password": "Student@12345"})
    response = client.get("/api/v1/trekker/exports/9999")
    assert response.status_code == 404
