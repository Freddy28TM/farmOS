import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import User
from backend.app.security import hash_password, verify_access_token


os.environ["FARMOS_JWT_SECRET"] = "test-secret-for-farmos"


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_test_user(
    email="farmer@example.com",
    password="FarmOS-test-password",
):
    db = TestingSessionLocal()

    user = User(
        email=email,
        password_hash=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id
    db.close()

    return user_id


def test_login_successfully_returns_access_token():
    reset_database()
    user_id = create_test_user()

    response = client.post(
        "/login",
        json={
            "email": "farmer@example.com",
            "password": "FarmOS-test-password",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]

    assert verify_access_token(data["access_token"]) == user_id


def test_login_rejects_wrong_password():
    reset_database()
    create_test_user()

    response = client.post(
        "/login",
        json={
            "email": "farmer@example.com",
            "password": "Wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_rejects_unknown_email():
    reset_database()

    response = client.post(
        "/login",
        json={
            "email": "unknown@example.com",
            "password": "FarmOS-test-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_normalizes_email():
    reset_database()
    user_id = create_test_user()

    response = client.post(
        "/login",
        json={
            "email": "  FARMER@EXAMPLE.COM  ",
            "password": "FarmOS-test-password",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    assert verify_access_token(token) == user_id


def test_login_does_not_expose_password_hash():
    reset_database()
    create_test_user()

    response = client.post(
        "/login",
        json={
            "email": "farmer@example.com",
            "password": "FarmOS-test-password",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "password" not in data
    assert "password_hash" not in data
