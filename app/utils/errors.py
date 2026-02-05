import logging
from functools import wraps
from typing import Dict, Any, Optional, Tuple, Callable

from flask import jsonify, Response, Flask, g
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ValidationError(AppError):
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, 400, details)


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, 404, {"resource": resource, "id": identifier})


class ConflictError(AppError):
    def __init__(self, message: str, resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(message, 409, details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


def error_response(error: AppError) -> Tuple[Response, int]:
    response: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": error.__class__.__name__,
            "message": error.message,
        },
    }
    if error.details:
        response["error"]["details"] = error.details
    return jsonify(response), error.status_code


def handle_controller_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle all errors in controller functions."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except (
            AppError,
            ValidationError,
            NotFoundError,
            ConflictError,
            UnauthorizedError,
            ForbiddenError,
        ):
            raise
        except IntegrityError as e:
            request_id = getattr(g, "request_id", "")
            logger.error(f"Database integrity error: {str(e)}: {request_id}")

            if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e):
                raise ConflictError("Resource already exists", "resource")
            elif "FOREIGN KEY constraint failed" in str(e):
                raise ValidationError("Referenced resource does not exist")
            else:
                raise AppError("Database constraint violation", 400)
        except DataError as e:
            request_id = getattr(g, "request_id", "")
            logger.error(f"Database data error: {str(e)}: {request_id}")
            raise ValidationError("Invalid data format")
        except SQLAlchemyError as e:
            request_id = getattr(g, "request_id", "")
            logger.error(f"Database error: {str(e)}: {request_id}")
            raise AppError("Database operation failed", 500)
        except Exception as e:
            request_id = getattr(g, "request_id", "")
            logger.error(f"Unexpected error: {str(e)}: {request_id}")
            raise

    return wrapper


def register_error_handlers(app: Flask) -> None:
    """Register all error handlers with the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError) -> Tuple[Response, int]:
        return error_response(error)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> Tuple[Response, int]:
        return error_response(error)

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error: NotFoundError) -> Tuple[Response, int]:
        return error_response(error)

    @app.errorhandler(ConflictError)
    def handle_conflict_error(error: ConflictError) -> Tuple[Response, int]:
        return error_response(error)

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(error: UnauthorizedError) -> Tuple[Response, int]:
        return error_response(error)

    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(error: ForbiddenError) -> Tuple[Response, int]:
        return error_response(error)

    @app.errorhandler(404)
    def handle_404(e: Any) -> Tuple[Response, int]:
        return jsonify({"error": {"message": "Resource not found"}}), 404

    @app.errorhandler(500)
    def handle_500(e: Any) -> Tuple[Response, int]:
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({"error": {"message": "Internal server error"}}), 500
