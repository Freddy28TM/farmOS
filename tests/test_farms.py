import os

os.environ["FARMOS_JWT_SECRET"] = "test-secret-for-farmos"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app import models
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


def test_authenticated_user_can_create_farm():
    user_id = create_test_user("farmer@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/farms",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "North Field",
            "latitude": -1.2921,
            "longitude": 36.8219,
            "crop": "maize",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["name"] == "North Field"
    assert data["latitude"] == -1.2921
    assert data["longitude"] == 36.8219
    assert data["crop"] == "maize"
    assert data["growth_stage"] == "vegetative"
    assert "user_id" not in data


def test_created_farm_belongs_to_authenticated_user():
    user_id = create_test_user("owner@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/farms",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Secure Farm",
            "latitude": -1.3,
            "longitude": 36.8,
            "crop": "maize",
            "growth_stage": "flowering",
        },
    )

    assert response.status_code == 201

    farm_id = response.json()["id"]

    db = TestingSessionLocal()

    farm = db.scalar(
        select(models.Farm).where(models.Farm.id == farm_id)
    )

    assert farm is not None
    assert farm.user_id == user_id

    db.close()


def test_unauthenticated_user_cannot_create_farm():
    response = client.post(
        "/farms",
        json={
            "name": "Unauthorized Farm",
            "latitude": -1.3,
            "longitude": 36.8,
            "crop": "maize",
            "growth_stage": "vegetative",
        },
    )

    assert response.status_code == 401


def test_client_cannot_override_farm_ownership():
    owner_id = create_test_user("realowner@example.com")
    attacker_id = create_test_user("anotheruser@example.com")

    token = create_access_token(owner_id)

    response = client.post(
        "/farms",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Owned Farm",
            "latitude": -1.3,
            "longitude": 36.8,
            "crop": "maize",
            "growth_stage": "vegetative",
            "user_id": attacker_id,
        },
    )

    assert response.status_code == 201

    farm_id = response.json()["id"]

    db = TestingSessionLocal()

    farm = db.scalar(
        select(models.Farm).where(models.Farm.id == farm_id)
    )

    assert farm is not None
    assert farm.user_id == owner_id
    assert farm.user_id != attacker_id

    db.close()


def test_invalid_farm_data_is_rejected():
    user_id = create_test_user("validator@example.com")
    token = create_access_token(user_id)

    response = client.post(
        "/farms",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "",
            "latitude": 100,
            "longitude": 36.8,
            "crop": "maize",
            "growth_stage": "invalid",
        },
    )

    assert response.status_code == 422
