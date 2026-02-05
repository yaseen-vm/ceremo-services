from typing import Dict, Any, Optional
from flask import Flask
from flask_cors import CORS
from app.config import Config, get_settings
from app.models.base import db
from app.repositories.rental_partner_repository import RentalPartnerRepository
from app.services.auth_service import AuthService
from app.routes.auth_routes import create_auth_routes
from app.utils.errors import register_error_handlers
from app.utils.logging import setup_request_logging
from flask_migrate import Migrate


def create_app(config: Optional[Config] = None) -> Flask:
    app = Flask(__name__)

    if config is None:
        config = get_settings()

    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = config.SECRET_KEY

    db.init_app(app)
    Migrate(app, db)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:8081"}})

    register_error_handlers(app)
    setup_request_logging(app)

    rental_partner_repo = RentalPartnerRepository()
    auth_service = AuthService(
        repository=rental_partner_repo,
        jwt_secret=config.JWT_SECRET_KEY,
        jwt_expiration=config.JWT_EXPIRATION_HOURS,
        refresh_expiration=config.REFRESH_TOKEN_EXPIRATION_HOURS,
        min_password_length=config.MIN_PASSWORD_LENGTH,
        remember_me_multiplier=config.REMEMBER_ME_MULTIPLIER,
    )

    auth_bp = create_auth_routes(auth_service)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.route("/")
    def index() -> Dict[str, Any]:
        return {"message": "Welcome to Ceremo Services", "status": "running"}

    @app.route("/health")
    def health_check() -> Dict[str, Any]:
        return {
            "status": "healthy",
            "environment": config.ENVIRONMENT,
            "database": "ceremo_db",
        }

    return app
