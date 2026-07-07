def test_chat_battery_agent_routing(client, auth_headers):
    resp = client.post("/api/chat", json={"message": "Show me low battery vehicles"}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent"] == "Battery Health Agent"
    assert "RJ14TEST01" in data["reply"]


def test_chat_maintenance_agent_routing(client, auth_headers):
    resp = client.post("/api/chat", json={"message": "Predict maintenance for the fleet"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["agent"] == "Maintenance Prediction Agent"


def test_chat_report_agent_routing(client, auth_headers):
    resp = client.post("/api/chat", json={"message": "Generate a weekly fleet summary report"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["agent"] == "Report Generator Agent"


def test_chat_rider_agent_routing(client, auth_headers):
    resp = client.post("/api/chat", json={"message": "Who are the worst performing riders?"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["agent"] == "Rider Performance Agent"


def test_chat_default_fleet_agent(client, auth_headers):
    resp = client.post("/api/chat", json={"message": "how are things going"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["agent"] == "Fleet Monitoring Agent"


def test_ml_maintenance_prediction_endpoint(client, auth_headers):
    resp = client.get("/api/ml/vehicle/1/maintenance-prediction", headers=auth_headers)
    assert resp.status_code == 200
    assert "maintenance_recommended" in resp.json()


def test_ml_delivery_delay_endpoint(client, auth_headers):
    resp = client.get("/api/ml/delivery-delay-risk?distance_km=10", headers=auth_headers)
    assert resp.status_code == 200
    assert "delay_risk" in resp.json()


def test_csv_export(client, auth_headers):
    resp = client.get("/api/reports/vehicles/csv", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")


def test_pdf_export(client, auth_headers):
    resp = client.get("/api/reports/fleet-summary/pdf", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_admin_route_requires_admin_role(client):
    reg = client.post(
        "/api/auth/register",
        json={"full_name": "Ops Guy", "email": "opsguy@evfleet.com", "password": "Pass@123", "role": "operations_manager"},
    )
    token = reg.json()["access_token"]
    resp = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
