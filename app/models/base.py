"""Base models and mixins."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from app.utils.timezone import now_ist


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True


db = SQLAlchemy(model_class=Base)


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps to models."""

    created_at = db.Column(db.DateTime(timezone=True), default=now_ist, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=now_ist,
        onupdate=now_ist,
        nullable=False,
    )
