"""Authentication routes."""

from typing import Any, Tuple
from flask import Blueprint, jsonify, g
from app.services.auth_service import AuthService
from app.contracts.auth_contracts import SignInRequest, SignUpRequest
from app.utils.validators import validate_json
from app.utils.errors import handle_controller_errors
from app.utils.logging import setup_logger

logger = setup_logger(__name__)


def create_auth_routes(auth_service: AuthService) -> Blueprint:
    """Create auth routes blueprint."""
    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/partner/signin", methods=["POST"])
    @validate_json(SignInRequest)
    @handle_controller_errors
    def sign_in() -> Tuple[Any, int]:
        """Sign in rental partner."""
        logger.info("Received sign in request")

        data = g.validated_json
        response = auth_service.sign_in(
            email=data["email"],
            password=data["password"],
            remember_me=data.get("rememberMe", False),
        )

        logger.info("Sign in successful")
        return jsonify(response.model_dump()), 200

    @auth_bp.route("/partner/signup", methods=["POST"])
    @validate_json(SignUpRequest)
    @handle_controller_errors
    def sign_up() -> Tuple[Any, int]:
        """Sign up rental partner."""
        logger.info("Received sign up request")

        data = g.validated_json
        response = auth_service.sign_up(
            email=data["email"],
            password=data["password"],
            confirm_password=data["confirmPassword"],
            first_name=data["firstName"],
            last_name=data["lastName"],
            phone=data["phone"],
            agree_to_terms=data["agreeToTerms"],
        )

        logger.info("Sign up successful")
        return jsonify(response.model_dump()), 201

    return auth_bp
