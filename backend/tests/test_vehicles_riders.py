def test_list_vehicles(client, auth_headers):
    resp = client.get("/api/vehicles", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_get_vehicle_by_id(client, auth_headers):
    resp = client.get("/api/vehicles/1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["registration_number"] == "RJ14TEST01"


def test_get_vehicle_not_found(client, auth_headers):
    resp = client.get("/api/vehicles/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_low_battery_vehicles(client, auth_headers):
    resp = client.get("/api/vehicles/low-battery/list", headers=auth_headers)
    assert resp.status_code == 200
    regs = [v["registration_number"] for v in resp.json()]
    assert "RJ14TEST01" in regs


def test_list_riders(client, auth_headers):
    resp = client.get("/api/riders", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_dashboard_kpis(client, auth_headers):
    resp = client.get("/api/dashboard/kpis", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_vehicles" in data
    assert "on_time_rate" in data


def test_vehicle_search_filter(client, auth_headers):
    resp = client.get("/api/vehicles?search=TEST01", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_pagination_bounds(client, auth_headers):
    resp = client.get("/api/vehicles?page=1&page_size=1", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1
