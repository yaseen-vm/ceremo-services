import pytest
from flask import Flask, g
from pydantic import BaseModel
from app.utils.validators import validate_query_params
from app.utils.errors import register_error_handlers


class QuerySchema(BaseModel):
    page: int
    limit: int


@pytest.fixture
def query_app():
    app = Flask(__name__)
    register_error_handlers(app)

    @app.route("/test", methods=["GET"])
    @validate_query_params(QuerySchema)
    def test_route():
        return {"data": g.validated_params}, 200

    return app


def test_validate_query_params_success(query_app):
    client = query_app.test_client()
    response = client.get("/test?page=1&limit=10")
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["page"] == 1
    assert data["data"]["limit"] == 10


def test_validate_query_params_missing_field(query_app):
    client = query_app.test_client()
    response = client.get("/test?page=1")
    assert response.status_code == 400


def test_validate_query_params_invalid_type(query_app):
    client = query_app.test_client()
    response = client.get("/test?page=invalid&limit=10")
    assert response.status_code == 400
