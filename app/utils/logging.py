import logging
import uuid
from typing import TYPE_CHECKING
from flask import g, request

if TYPE_CHECKING:
    from flask import Flask


class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request ID in log messages"""

    def format(self, record: logging.LogRecord) -> str:
        try:
            record.request_id = getattr(g, "request_id", "")
        except RuntimeError:
            record.request_id = ""
        return super().format(record)


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with request-aware formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = RequestFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
    )

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def setup_request_logging(app: "Flask") -> None:
    """Set up request ID generation for logging context"""

    @app.before_request
    def generate_request_id() -> None:
        g.request_id = str(uuid.uuid4())
