"""Rental Partner domain model."""

import uuid
from app.models.base import db, BaseModel, TimestampMixin


class RentalPartner(BaseModel, TimestampMixin):
    __tablename__ = "rental_partners"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    __table_args__ = (db.Index("idx_rental_partners_email", "email"),)
