def login_admin(client):
    client.post("/api/v1/auth/login", json={"email": "admin@test.local", "password": "Admin@12345"})


def test_admin_can_create_and_approve_trek(client):
    login_admin(client)
    payload = {
        "name": "New Trek",
        "location": "Nashik",
        "difficulty": "HARD",
        "duration_days": 2,
        "capacity": 8,
        "available_slots": 8,
        "start_date": "2027-01-10",
        "end_date": "2027-01-11",
        "price": 1500,
    }
    response = client.post("/api/v1/admin/treks", json=payload)
    assert response.status_code == 201
    trek_id = response.json["data"]["id"]
    response = client.post(f"/api/v1/admin/treks/{trek_id}/approve")
    assert response.status_code == 200
    assert response.json["data"]["status"] == "APPROVED"


def test_admin_can_blacklist_trekker(client):
    login_admin(client)
    response = client.patch("/api/v1/admin/users/3/status", json={"status": "BLACKLISTED"})
    assert response.status_code == 200
    assert response.json["data"]["status"] == "BLACKLISTED"
