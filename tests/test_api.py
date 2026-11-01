import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_overview_endpoint():
    res = client.get("/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_bookings"] == 119390
    assert data["canceled_bookings"] == 44224

def test_hotels_endpoint():
    res = client.get("/analytics/hotels")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2

def test_cancellations_lead_time_endpoint():
    res = client.get("/analytics/cancellations/lead-time")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 5

def test_revenue_monthly_endpoint():
    res = client.get("/analytics/revenue/monthly")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 26

def test_channels_performance_endpoint():
    res = client.get("/analytics/channels/performance")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 5

def test_guests_composition_endpoint():
    res = client.get("/analytics/guests/composition")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4

def test_rooms_reassignment_endpoint():
    res = client.get("/analytics/rooms/reassignment-summary")
    assert res.status_code == 200
    data = res.json()
    assert data["reassigned_bookings"] == 14917
