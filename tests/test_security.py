import pytest

from backend.app.security import (
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password,
)


def test_password_is_hashed():
    password = "FarmOS-test-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert isinstance(hashed_password, str)


def test_correct_password_verifies():
    password = "FarmOS-test-password"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)


def test_incorrect_password_fails():
    password = "FarmOS-test-password"
    wrong_password = "Wrong-password"

    hashed_password = hash_password(password)

    assert not verify_password(
        wrong_password,
        hashed_password,
    )


def test_same_password_generates_different_hashes():
    password = "FarmOS-test-password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_hash_can_be_verified_after_multiple_hashes():
    password = "FarmOS-test-password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)


def test_access_token_contains_user_id(monkeypatch):
    monkeypatch.setenv(
        "FARMOS_JWT_SECRET",
        "test-secret-for-farmos",
    )

    token = create_access_token(user_id=42)

    assert isinstance(token, str)
    assert verify_access_token(token) == 42


def test_access_token_rejects_tampering(monkeypatch):
    monkeypatch.setenv(
        "FARMOS_JWT_SECRET",
        "test-secret-for-farmos",
    )

    token = create_access_token(user_id=42)

    parts = token.split(".")

    assert len(parts) == 3

    tampered_payload = (
        parts[1][:-1]
        + ("a" if parts[1][-1] != "a" else "b")
    )

    tampered_token = ".".join(
        [
            parts[0],
            tampered_payload,
            parts[2],
        ]
    )

    with pytest.raises(
        ValueError,
        match="Invalid access token",
    ):
        verify_access_token(tampered_token)


def test_access_token_requires_secret(monkeypatch):
    monkeypatch.delenv(
        "FARMOS_JWT_SECRET",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match="FARMOS_JWT_SECRET",
    ):
        create_access_token(user_id=42)


def test_invalid_access_token_is_rejected(monkeypatch):
    monkeypatch.setenv(
        "FARMOS_JWT_SECRET",
        "test-secret-for-farmos",
    )

    with pytest.raises(
        ValueError,
        match="Invalid access token",
    ):
        verify_access_token("not-a-real-token")
