from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import User
from backend.app.security import verify_password


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    return engine, Session()


def test_register_user():
    engine, db_session = create_test_session()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/register",
            json={
                "email": "farmer@example.com",
                "password": "FarmOS-test-password",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert data["email"] == "farmer@example.com"
        assert "password" not in data
        assert "password_hash" not in data

        user = db_session.scalar(
            select(User).where(
                User.email == "farmer@example.com"
            )
        )

        assert user is not None
        assert user.password_hash != "FarmOS-test-password"
        assert verify_password(
            "FarmOS-test-password",
            user.password_hash,
        )
    finally:
        app.dependency_overrides.clear()
        db_session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_register_duplicate_email():
    engine, db_session = create_test_session()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        first_response = client.post(
            "/register",
            json={
                "email": "farmer@example.com",
                "password": "FarmOS-test-password",
            },
        )

        second_response = client.post(
            "/register",
            json={
                "email": "farmer@example.com",
                "password": "Another-password",
            },
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json()["detail"] == (
            "Email is already registered"
        )
    finally:
        app.dependency_overrides.clear()
        db_session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_register_normalizes_email():
    engine, db_session = create_test_session()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/register",
            json={
                "email": "  FARMER@EXAMPLE.COM  ",
                "password": "FarmOS-test-password",
            },
        )

        assert response.status_code == 201
        assert response.json()["email"] == "farmer@example.com"

        user = db_session.scalar(
            select(User).where(
                User.email == "farmer@example.com"
            )
        )

        assert user is not None
    finally:
        app.dependency_overrides.clear()
        db_session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_register_rejects_short_password():
    engine, db_session = create_test_session()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/register",
            json={
                "email": "farmer@example.com",
                "password": "short",
            },
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
        db_session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_register_rejects_invalid_email():
    engine, db_session = create_test_session()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/register",
            json={
                "email": "not-an-email",
                "password": "FarmOS-test-password",
            },
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
        db_session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
