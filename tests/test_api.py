import os

os.environ["FARMOS_JWT_SECRET"] = "test-secret-for-farmos"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import models
from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.security import create_access_token, hash_password


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_test_user(email):
    db = TestingSessionLocal()

    user = models.User(
        email=email,
        password_hash=hash_password("password123"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    db.close()

    return user_id


def create_test_farm(
    user_id,
    name="Test Farm",
    latitude=-1.286389,
    longitude=36.817223,
    crop="maize",
    growth_stage="vegetative",
):
    db = TestingSessionLocal()

    farm = models.Farm(
        user_id=user_id,
        name=name,
        latitude=latitude,
        longitude=longitude,
        crop=crop,
        growth_stage=growth_stage,
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    farm_id = farm.id

    db.close()

    return farm_id


def cleanup_database():
    db = TestingSessionLocal()

    db.query(models.RiskAssessment).delete()
    db.query(models.Farm).delete()
    db.query(models.User).delete()

    db.commit()
    db.close()


client = TestClient(app)


import pytest


@pytest.fixture(autouse=True)
def override_database():
    cleanup_database()

    previous_override = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_db] = override_get_db

    yield

    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "FarmOS API is running"
    }


def test_water_risk_requires_authentication():
    response = client.post(
        "/water-risk",
        json={"farm_id": 1},
    )

    assert response.status_code == 401


def test_water_risk_creates_persistent_assessment(monkeypatch):
    def fake_environmental_data(latitude, longitude):
        assert latitude == -1.286389
        assert longitude == 36.817223

        return {
            "temperature": 35,
            "recent_rainfall": 2,
            "forecast_rainfall": 2,
        }

    monkeypatch.setattr(
        "backend.app.main.get_environmental_data",
        fake_environmental_data,
    )

    user_id = create_test_user("farmer@example.com")
    token = create_access_token(user_id)

    farm_id = create_test_farm(
        user_id=user_id,
        growth_stage="vegetative",
    )

    response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {token}"},
        json={"farm_id": farm_id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["assessment_id"] > 0
    assert data["risk_level"] == "HIGH"
    assert data["score"] == 7
    assert data["confidence"] == "MEDIUM"

    db = TestingSessionLocal()

    assessment = db.scalar(
        select(models.RiskAssessment).where(
            models.RiskAssessment.id == data["assessment_id"]
        )
    )

    assert assessment is not None
    assert assessment.farm_id == farm_id
    assert assessment.recent_rainfall == 2
    assert assessment.forecast_rainfall == 2
    assert assessment.temperature == 35
    assert assessment.risk_level == "HIGH"
    assert assessment.score == 7
    assert assessment.confidence == "MEDIUM"

    db.close()


def test_water_risk_uses_stored_farm_context(monkeypatch):
    captured = {}

    def fake_environmental_data(latitude, longitude):
        captured["latitude"] = latitude
        captured["longitude"] = longitude

        return {
            "temperature": 24,
            "recent_rainfall": 30,
            "forecast_rainfall": 30,
        }

    monkeypatch.setattr(
        "backend.app.main.get_environmental_data",
        fake_environmental_data,
    )

    user_id = create_test_user("context@example.com")
    token = create_access_token(user_id)

    farm_id = create_test_farm(
        user_id=user_id,
        latitude=-1.3,
        longitude=36.8,
        crop="maize",
        growth_stage="flowering",
    )

    response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {token}"},
        json={"farm_id": farm_id},
    )

    assert response.status_code == 200

    data = response.json()

    assert captured["latitude"] == -1.3
    assert captured["longitude"] == 36.8
    assert data["risk_level"] == "LOW"
    assert data["score"] == 0
    assert "Crop: maize" in data["context"]
    assert "Growth stage: flowering" in data["context"]


def test_water_risk_rejects_nonexistent_farm():
    user_id = create_test_user("missing@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {token}"},
        json={"farm_id": 999999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Farm not found"


def test_water_risk_cannot_access_another_users_farm():
    owner_id = create_test_user("owner@example.com")
    attacker_id = create_test_user("attacker@example.com")

    farm_id = create_test_farm(
        user_id=owner_id,
        name="Private Farm",
    )

    attacker_token = create_access_token(attacker_id)

    response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {attacker_token}"},
        json={"farm_id": farm_id},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Farm not found"


def test_water_risk_missing_farm_id_is_rejected():
    user_id = create_test_user("missing-field@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert response.status_code == 422

    error = response.json()

    assert error["detail"][0]["loc"][-1] == "farm_id"


def test_water_risk_rejects_invalid_farm_id():
    user_id = create_test_user("invalid-id@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {token}"},
        json={"farm_id": 0},
    )

    assert response.status_code == 422


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

    user_id = create_test_user("fields@example.com")
    token = create_access_token(user_id)
    farm_id = create_test_farm(user_id)

    response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {token}"},
        json={"farm_id": farm_id},
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "assessment_id",
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

    user_id = create_test_user("failure@example.com")
    token = create_access_token(user_id)
    farm_id = create_test_farm(user_id)

    response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {token}"},
        json={"farm_id": farm_id},
    )

    assert response.status_code == 503

    error = response.json()

    assert error["detail"] == (
        "Environmental data is missing temperature"
    )

def test_feedback_requires_authentication():
    response = client.post(
        "/risk-assessments/1/feedback",
        json={
            "farmer_action": "Monitored soil moisture",
            "observed_result": "Crop remained healthy",
        },
    )

    assert response.status_code == 401


def test_feedback_is_persisted(monkeypatch):
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

    user_id = create_test_user("feedback@example.com")
    token = create_access_token(user_id)
    farm_id = create_test_farm(user_id)

    assessment_response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {token}"},
        json={"farm_id": farm_id},
    )

    assert assessment_response.status_code == 200

    assessment_id = assessment_response.json()["assessment_id"]

    feedback_response = client.post(
        f"/risk-assessments/{assessment_id}/feedback",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "farmer_action": "Monitored soil moisture",
            "observed_result": "Crop remained healthy",
        },
    )

    assert feedback_response.status_code == 200

    data = feedback_response.json()

    assert data["assessment_id"] == assessment_id
    assert data["farmer_action"] == "Monitored soil moisture"
    assert data["observed_result"] == "Crop remained healthy"
    assert data["feedback_submitted_at"]

    db = TestingSessionLocal()

    assessment = db.scalar(
        select(models.RiskAssessment).where(
            models.RiskAssessment.id == assessment_id
        )
    )

    assert assessment is not None
    assert assessment.farmer_action == "Monitored soil moisture"
    assert assessment.observed_result == "Crop remained healthy"
    assert assessment.feedback_submitted_at is not None

    db.close()


def test_feedback_cannot_access_another_users_assessment(
    monkeypatch,
):
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

    owner_id = create_test_user("feedback-owner@example.com")
    attacker_id = create_test_user("feedback-attacker@example.com")

    owner_token = create_access_token(owner_id)
    attacker_token = create_access_token(attacker_id)

    farm_id = create_test_farm(owner_id)

    assessment_response = client.post(
        "/water-risk",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"farm_id": farm_id},
    )

    assert assessment_response.status_code == 200

    assessment_id = assessment_response.json()["assessment_id"]

    feedback_response = client.post(
        f"/risk-assessments/{assessment_id}/feedback",
        headers={"Authorization": f"Bearer {attacker_token}"},
        json={
            "farmer_action": "Unauthorized action",
            "observed_result": "Unauthorized result",
        },
    )

    assert feedback_response.status_code == 404
    assert feedback_response.json()["detail"] == (
        "Risk assessment not found"
    )


def test_feedback_rejects_missing_fields():
    user_id = create_test_user("invalid-feedback@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/risk-assessments/1/feedback",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert response.status_code == 422


def test_feedback_rejects_empty_values():
    user_id = create_test_user("empty-feedback@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/risk-assessments/1/feedback",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "farmer_action": "",
            "observed_result": "",
        },
    )

    assert response.status_code == 422


def test_feedback_rejects_nonexistent_assessment():
    user_id = create_test_user("missing-assessment@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/risk-assessments/999999/feedback",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "farmer_action": "Monitored the farm",
            "observed_result": "Everything was normal",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Risk assessment not found"
    )
