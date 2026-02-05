import pytest
import json
from flask import Flask, g
from pydantic import BaseModel
from app.utils.validators import validate_json
from app.utils.errors import ValidationError, register_error_handlers


class SampleSchema(BaseModel):
    name: str
    age: int


@pytest.fixture
def test_app():
    app = Flask(__name__)
    register_error_handlers(app)

    @app.route("/test", methods=["POST"])
    @validate_json(SampleSchema)
    def test_route():
        return {"data": g.validated_json}, 200

    return app


def test_validate_json_success(test_app):
    client = test_app.test_client()
    response = client.post(
        "/test", json={"name": "John", "age": 30}, content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["name"] == "John"
    assert data["data"]["age"] == 30


def test_validate_json_missing_field(test_app):
    client = test_app.test_client()
    response = client.post(
        "/test", json={"name": "John"}, content_type="application/json"
    )
    assert response.status_code == 400


def test_validate_json_invalid_type(test_app):
    client = test_app.test_client()
    response = client.post(
        "/test",
        json={"name": "John", "age": "invalid"},
        content_type="application/json",
    )
    assert response.status_code == 400


def test_validate_json_not_json(test_app):
    client = test_app.test_client()
    response = client.post("/test", data="not json", content_type="text/plain")
    assert response.status_code == 400


def test_validate_json_empty_body(test_app):
    client = test_app.test_client()
    response = client.post("/test", data="", content_type="application/json")
    assert response.status_code == 400


def test_validate_json_malformed_json(test_app):
    client = test_app.test_client()
    response = client.post(
        "/test", data="{invalid json}", content_type="application/json"
    )
    assert response.status_code == 400
