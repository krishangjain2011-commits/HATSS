"""Database engine and dependency primitives."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Create the shared engine lazily so liveness does not require PostgreSQL."""
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Return a configured session factory for future request dependencies."""
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def get_db_session() -> Generator[Session, None, None]:
    """Yield one transaction boundary for a request and always close it."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
