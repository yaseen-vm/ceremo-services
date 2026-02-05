import pytest
import jwt
from datetime import datetime, timedelta
from app.utils.security import hash_password, verify_password, generate_token


def test_hash_password():
    password = "test_password"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0


def test_verify_password_correct():
    password = "test_password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    password = "test_password"
    hashed = hash_password(password)
    assert verify_password("wrong_password", hashed) is False


def test_generate_token():
    user_id = "test-user-id"
    secret = "test-secret-key-at-least-32-chars-long-for-security"
    expiration = 24

    token = generate_token(user_id, secret, expiration)
    assert token is not None
    assert len(token) > 0

    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    assert decoded["user_id"] == user_id
    assert "exp" in decoded
    assert "iat" in decoded


def test_generate_token_expiration():
    user_id = "test-user-id"
    secret = "test-secret-key-at-least-32-chars-long-for-security"
    expiration = 1

    token = generate_token(user_id, secret, expiration)
    decoded = jwt.decode(token, secret, algorithms=["HS256"])

    exp_time = datetime.fromtimestamp(decoded["exp"])
    iat_time = datetime.fromtimestamp(decoded["iat"])
    diff = exp_time - iat_time

    assert diff.total_seconds() == pytest.approx(3600, rel=1)
