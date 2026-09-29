def test_public_trek_endpoint_works_without_redis(client):
    response = client.get("/api/v1/treks")
    assert response.status_code == 200
    assert len(response.json["data"]) == 1
