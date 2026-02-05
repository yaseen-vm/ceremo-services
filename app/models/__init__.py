"""Models package."""

from app.models.base import db, BaseModel, TimestampMixin
from app.models.rental_partner import RentalPartner

__all__ = ["db", "BaseModel", "TimestampMixin", "RentalPartner"]
