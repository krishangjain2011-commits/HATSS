"""SQLAlchemy declarative metadata for future domain models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for HATSS persistence models."""
