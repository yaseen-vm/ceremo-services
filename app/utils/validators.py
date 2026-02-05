"""Request validation utilities."""

import json
from functools import wraps
from typing import Any, Callable, Type

from flask import request, g
from pydantic import BaseModel, ValidationError as PydanticValidationError

from app.utils.errors import ValidationError


def validate_json(schema: Type[BaseModel]) -> Callable[..., Any]:
    """Decorator to validate JSON request body against Pydantic schema."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not request.is_json:
                raise ValidationError("Content-Type must be application/json")

            try:
                data = request.get_json()
                if data is None:
                    raise ValidationError("Request body must contain valid JSON")

                validated = schema(**data)
                g.validated_json = validated.model_dump()

            except PydanticValidationError as e:
                errors = []
                for error in e.errors():
                    field = ".".join(str(loc) for loc in error["loc"])
                    errors.append(f"{field}: {error['msg']}")
                raise ValidationError("; ".join(errors))
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON format")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_query_params(schema: Type[BaseModel]) -> Callable[..., Any]:
    """Decorator to validate query parameters against Pydantic schema."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                validated = schema(**request.args.to_dict())
                g.validated_params = validated.model_dump()

            except PydanticValidationError as e:
                errors = []
                for error in e.errors():
                    field = ".".join(str(loc) for loc in error["loc"])
                    errors.append(f"{field}: {error['msg']}")
                raise ValidationError("; ".join(errors))

            return func(*args, **kwargs)

        return wrapper

    return decorator
