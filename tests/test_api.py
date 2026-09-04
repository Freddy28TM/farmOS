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


def test_water_risk_rejects_unsupported_crop():
    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "longitude": 36.817223,
            "crop": "banana",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 422


def test_water_risk_rejects_unsupported_growth_stage():
    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "longitude": 36.817223,
            "crop": "maize",
            "growth_stage": "unknown",
        },
    )

    assert response.status_code == 422


def test_water_risk_invalid_crop_error_identifies_field():
    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "longitude": 36.817223,
            "crop": "banana",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 422

    error = response.json()

    assert error["detail"][0]["loc"][-1] == "crop"
    assert "Crop must be maize" in error["detail"][0]["msg"]


def test_water_risk_response_has_expected_fields(monkeypatch):
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

    assert set(data.keys()) == {
        "risk_level",
        "score",
        "confidence",
        "factors",
        "recommendation",
        "explanation",
        "context",
    }


def test_water_risk_handles_environmental_data_failure(monkeypatch):
    def fake_environmental_data(latitude, longitude):
        raise ValueError(
            "Environmental data is missing temperature"
        )

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

    assert response.status_code == 503

    error = response.json()

    assert error["detail"] == (
        "Environmental data is missing temperature"
    )


def test_water_risk_rejects_missing_latitude():
    response = client.post(
        "/water-risk",
        json={
            "longitude": 36.817223,
            "crop": "maize",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 422

    error = response.json()

    assert error["detail"][0]["loc"][-1] == "latitude"


def test_water_risk_rejects_missing_longitude():
    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "crop": "maize",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 422

    error = response.json()

    assert error["detail"][0]["loc"][-1] == "longitude"


def test_water_risk_rejects_missing_crop():
    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "longitude": 36.817223,
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 422

    error = response.json()

    assert error["detail"][0]["loc"][-1] == "crop"


def test_water_risk_rejects_missing_growth_stage():
    response = client.post(
        "/water-risk",
        json={
            "latitude": -1.286389,
            "longitude": 36.817223,
            "crop": "maize",
        },
    )

    assert response.status_code == 422

    error = response.json()

    assert error["detail"][0]["loc"][-1] == "growth_stage"


def test_water_risk_handles_environmental_network_failure(monkeypatch):
    def failing_environmental_data(latitude, longitude):
        raise ValueError(
            "Environmental data request failed"
        )

    monkeypatch.setattr(
        "backend.app.main.get_environmental_data",
        failing_environmental_data,
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

    assert response.status_code == 503

    error = response.json()

    assert error["detail"] == (
        "Environmental data request failed"
    )
