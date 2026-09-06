import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import User
from backend.app.security import create_access_token, hash_password


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


def test_me_returns_authenticated_user():
    reset_database()

    user_id = create_test_user()

    token = create_access_token(user_id)

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["email"] == "farmer@example.com"
    assert "password_hash" not in data


def test_me_rejects_missing_token():
    reset_database()

    response = client.get("/me")

    assert response.status_code == 401


def test_me_rejects_invalid_token():
    reset_database()

    response = client.get(
        "/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_me_rejects_token_for_nonexistent_user():
    reset_database()

    token = create_access_token(user_id=999999)

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401
