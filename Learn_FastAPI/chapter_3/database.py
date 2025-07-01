"""
Database Configuration Module
-----------------------------

This module sets up the SQLAlchemy engine, session factory, and base model
class for ORM mappings using an SQLite database.

Key Features:
- Uses SQLite with a relative file path.
- Disables SQLite thread checks for use in multithreaded environments (e.g., FastAPI).
- Provides a reusable session dependency for database access.
- Defines a declarative base class for all SQLAlchemy ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator

# SQLite database URL using a relative path.
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

# Create a SQLAlchemy engine.
# The 'check_same_thread=False' option is specific to SQLite and allows access across threads.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured session factory.
# - autocommit=False ensures changes are committed manually.
# - autoflush=False disables automatic flushing of changes.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    All models should inherit from this class to be recognized by SQLAlchemy
    when creating database tables.
    """

    pass


def get_db() -> Generator:
    """
    Dependency function to get a database session.

    Yields:
        A SQLAlchemy SessionLocal instance.

    This function is designed to be used with FastAPI's dependency injection
    system. It ensures that each request gets its own database session,
    which is properly closed after the request is handled.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
