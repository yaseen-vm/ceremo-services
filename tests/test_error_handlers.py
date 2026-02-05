import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError
from app.utils.errors import (
    handle_controller_errors,
    AppError,
    ConflictError,
    ValidationError,
)


@pytest.fixture
def test_app():
    app = Flask(__name__)
    return app


def test_handle_controller_errors_integrity_unique(test_app):
    with test_app.app_context():

        @handle_controller_errors
        def func():
            raise IntegrityError("statement", "params", "Duplicate entry 'test'")

        with pytest.raises(ConflictError):
            func()


def test_handle_controller_errors_integrity_unique_constraint(test_app):
    with test_app.app_context():

        @handle_controller_errors
        def func():
            raise IntegrityError("statement", "params", "UNIQUE constraint failed")

        with pytest.raises(ConflictError):
            func()


def test_handle_controller_errors_integrity_foreign_key(test_app):
    with test_app.app_context():

        @handle_controller_errors
        def func():
            raise IntegrityError("statement", "params", "FOREIGN KEY constraint failed")

        with pytest.raises(ValidationError):
            func()


def test_handle_controller_errors_integrity_other(test_app):
    with test_app.app_context():

        @handle_controller_errors
        def func():
            raise IntegrityError("statement", "params", "other error")

        with pytest.raises(AppError):
            func()


def test_handle_controller_errors_data_error(test_app):
    with test_app.app_context():

        @handle_controller_errors
        def func():
            raise DataError("statement", "params", "data error")

        with pytest.raises(ValidationError):
            func()


def test_handle_controller_errors_sqlalchemy_error(test_app):
    with test_app.app_context():

        @handle_controller_errors
        def func():
            raise SQLAlchemyError("database error")

        with pytest.raises(AppError):
            func()


def test_handle_controller_errors_unexpected(test_app):
    with test_app.app_context():

        @handle_controller_errors
        def func():
            raise RuntimeError("unexpected error")

        with pytest.raises(RuntimeError):
            func()
