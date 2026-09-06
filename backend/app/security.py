import os
from datetime import datetime, timedelta, UTC

import jwt
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using the recommended
    password-hashing algorithm.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its stored hash.
    """
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    """
    Create a signed JWT access token for a user.

    The JWT secret must be provided through the
    FARMOS_JWT_SECRET environment variable.
    """
    secret = os.getenv("FARMOS_JWT_SECRET")

    if not secret:
        raise RuntimeError(
            "FARMOS_JWT_SECRET environment variable is not set"
        )

    expires_at = datetime.now(UTC) + timedelta(
        minutes=JWT_EXPIRATION_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        secret,
        algorithm=JWT_ALGORITHM,
    )


def verify_access_token(token: str) -> int:
    """
    Verify a JWT access token and return its user ID.

    Raises RuntimeError if the JWT secret is missing.
    Raises ValueError if the token is invalid or expired.
    """
    secret = os.getenv("FARMOS_JWT_SECRET")

    if not secret:
        raise RuntimeError(
            "FARMOS_JWT_SECRET environment variable is not set"
        )

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError as error:
        raise ValueError("Invalid access token") from error

    user_id = payload.get("sub")

    if user_id is None:
        raise ValueError("Invalid access token")

    try:
        return int(user_id)
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid access token") from error
