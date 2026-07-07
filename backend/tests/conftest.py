import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = "sqlite:///./test_fleet.db"

from app.main import app  # noqa: E402
from app.db.database import Base, engine, SessionLocal  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.models.vehicle import Vehicle, VehicleStatus  # noqa: E402
from app.models.rider import Rider, RiderStatus  # noqa: E402
from app.core.security import hash_password  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(User(full_name="Test Admin", email="test-admin@evfleet.com", hashed_password=hash_password("Test@123"), role=UserRole.admin))
    db.add(Vehicle(registration_number="RJ14TEST01", model="Zypp Zomo E1", city="Jaipur", status=VehicleStatus.active, battery_level=15.0, battery_health=60.0, odometer_km=21000))
    db.add(Rider(full_name="Test Rider", phone="9999999999", city="Jaipur", status=RiderStatus.active, performance_score=45.0))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_fleet.db"):
        os.remove("test_fleet.db")


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_token(client):
    resp = client.post("/api/auth/login", json={"email": "test-admin@evfleet.com", "password": "Test@123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
