from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "FarmOS API is running"
    }


def test_water_risk_high():
    response = client.post(
        "/water-risk",
        json={
            "recent_rainfall": 2,
            "forecast_rainfall": 2,
            "temperature": 35,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "HIGH"
    assert data["score"] == 6


def test_water_risk_low():
    response = client.post(
        "/water-risk",
        json={
            "recent_rainfall": 30,
            "forecast_rainfall": 30,
            "temperature": 24,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "LOW"
    assert data["score"] == 0
