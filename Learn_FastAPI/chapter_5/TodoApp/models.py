"""
SQLAlchemy models for the FastAPI application in Chapter 5.

Defines the Users and Todos tables.
"""

from .database import Base
from pydantic import ConfigDict
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    """
    SQLAlchemy model for the users table.

    Fields:
        id: Primary key, unique user identifier.
        email: Unique email address of the user.
        username: Unique username.
        first_name: User's first name.
        last_name: User's last name.
        hashed_password: Hashed password for authentication.
        is_active: Boolean indicating if the user is active.
        role: Role of the user (e.g., admin, user).
        phone_number: User's phone number.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)
    model_config = ConfigDict(from_attributes=True)


class Todos(Base):
    """
    SQLAlchemy model for the todos table.

    Fields:
        id: Primary key, unique todo identifier.
        title: Title of the todo item.
        description: Description of the todo item.
        priority: Priority level of the todo.
        complete: Boolean indicating if the todo is complete.
        owner_id: Foreign key referencing the user who owns the todo.
    """

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    model_config = ConfigDict(from_attributes=True)
