def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_and_login(client):
    resp = client.post(
        "/api/auth/register",
        json={"full_name": "New User", "email": "newuser@evfleet.com", "password": "Pass@123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["email"] == "newuser@evfleet.com"
    assert "access_token" in data

    resp2 = client.post("/api/auth/login", json={"email": "newuser@evfleet.com", "password": "Pass@123"})
    assert resp2.status_code == 200


def test_login_wrong_password(client):
    resp = client.post("/api/auth/login", json={"email": "test-admin@evfleet.com", "password": "wrong"})
    assert resp.status_code == 401


def test_duplicate_registration_rejected(client):
    client.post("/api/auth/register", json={"full_name": "Dup", "email": "dup@evfleet.com", "password": "Pass@123"})
    resp = client.post("/api/auth/register", json={"full_name": "Dup2", "email": "dup@evfleet.com", "password": "Pass@123"})
    assert resp.status_code == 400


def test_protected_route_requires_token(client):
    resp = client.get("/api/vehicles")
    assert resp.status_code == 401


def test_me_endpoint(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test-admin@evfleet.com"
