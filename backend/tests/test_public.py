def test_public_trek_search(client):
    response = client.get("/api/v1/treks?location=Pune")
    assert response.status_code == 200
    assert response.json["data"][0]["location"] == "Pune"


def test_public_invalid_status_returns_400(client):
    response = client.get("/api/v1/treks?status=UNKNOWN")
    assert response.status_code == 400
