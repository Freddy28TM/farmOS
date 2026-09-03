from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "FarmOS API is running"
    }


def test_water_risk_high(monkeypatch):
    def fake_environmental_data(latitude, longitude):
        return {
            "temperature": 35,
            "recent_rainfall": 2,
            "forecast_rainfall": 2,
        }

    monkeypatch.setattr(
        "backend.app.main.get_environmental_data",
        fake_environmental_data,
    )

    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "longitude": 36.817223,
            "crop": "maize",
             "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "HIGH"
    assert data["score"] == 7


def test_water_risk_low(monkeypatch):
    def fake_environmental_data(latitude, longitude):
        return {
            "temperature": 24,
            "recent_rainfall": 30,
            "forecast_rainfall": 30,
        }

    monkeypatch.setattr(
        "backend.app.main.get_environmental_data",
        fake_environmental_data,
    )

    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "longitude": 36.817223,
            "crop": "maize",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "LOW"
    assert data["score"] == 0

def test_water_risk_rejects_invalid_latitude():
    response = client.post(
        "/water-risk",
        json={
            "latitude": 100,
            "longitude": 36.817223,
            "crop": "maize",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 422

def test_water_risk_rejects_invalid_longitude():
    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "longitude": 200,
            "crop": "maize",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 422
