import pytest
from app import create_app
from app.config import Config


@pytest.fixture
def test_config():
    return Config(
        DATABASE_HOST="test_host",
        DATABASE_PORT=3307,
        DATABASE_USER="test_user",
        DATABASE_PASSWORD="test_pass",
        DATABASE_NAME="test_db",
        ENVIRONMENT="test",
        DEBUG=True,
        SECRET_KEY="test-secret",
        JWT_SECRET_KEY="test-jwt-secret",
        JWT_EXPIRATION_HOURS=24,
        REFRESH_TOKEN_EXPIRATION_HOURS=720,
        MIN_PASSWORD_LENGTH=8,
        REMEMBER_ME_MULTIPLIER=24,
    )


@pytest.fixture
def app(test_config):
    return create_app(test_config)


@pytest.fixture
def client(app):
    return app.test_client()
