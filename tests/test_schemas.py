import pytest
from app.schemas import __all__


def test_schemas_module_exports():
    assert isinstance(__all__, list)
    assert len(__all__) == 0
