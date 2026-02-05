import pytest
from unittest.mock import Mock
from flask import Flask
from app.routes.auth_routes import create_auth_routes
from app.contracts.auth_contracts import AuthResponse, AuthData, UserData
from app.utils.errors import register_error_handlers


@pytest.fixture
def mock_auth_service():
    return Mock()


@pytest.fixture
def auth_client(mock_auth_service):
    app = Flask(__name__)
    register_error_handlers(app)
    auth_bp = create_auth_routes(mock_auth_service)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    return app.test_client(), mock_auth_service


def test_sign_in_success(auth_client):
    client, mock_auth_service = auth_client
    user_data = UserData(
        id="test-id",
        email="test@example.com",
        firstName="John",
        lastName="Doe",
        phone="1234567890",
    )
    auth_data = AuthData(user=user_data, token="token", refreshToken="refresh")
    mock_auth_service.sign_in.return_value = AuthResponse(
        data=auth_data, message="Sign in successful"
    )

    response = client.post(
        "/api/auth/partner/signin",
        json={"email": "test@example.com", "password": "password123"},
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "test@example.com"


def test_sign_in_invalid_json(auth_client):
    client, _ = auth_client
    response = client.post(
        "/api/auth/partner/signin",
        data="invalid",
        content_type="application/json",
    )
    assert response.status_code == 400


def test_sign_in_missing_fields(auth_client):
    client, _ = auth_client
    response = client.post(
        "/api/auth/partner/signin",
        json={"email": "test@example.com"},
        content_type="application/json",
    )
    assert response.status_code == 400


def test_sign_up_success(auth_client):
    client, mock_auth_service = auth_client
    user_data = UserData(
        id="test-id",
        email="test@example.com",
        firstName="John",
        lastName="Doe",
        phone="1234567890",
    )
    auth_data = AuthData(user=user_data, token="token", refreshToken="refresh")
    mock_auth_service.sign_up.return_value = AuthResponse(
        data=auth_data, message="Registration successful"
    )

    response = client.post(
        "/api/auth/partner/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
            "confirmPassword": "password123",
            "firstName": "John",
            "lastName": "Doe",
            "phone": "1234567890",
            "agreeToTerms": True,
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True


def test_sign_up_missing_fields(auth_client):
    client, _ = auth_client
    response = client.post(
        "/api/auth/partner/signup",
        json={"email": "test@example.com", "password": "password123"},
        content_type="application/json",
    )
    assert response.status_code == 400


def test_sign_up_invalid_email(auth_client):
    client, _ = auth_client
    response = client.post(
        "/api/auth/partner/signup",
        json={
            "email": "invalid-email",
            "password": "password123",
            "confirmPassword": "password123",
            "firstName": "John",
            "lastName": "Doe",
            "phone": "1234567890",
            "agreeToTerms": True,
        },
        content_type="application/json",
    )
    assert response.status_code == 400
