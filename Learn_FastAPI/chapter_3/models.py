"""
SQLAlchemy ORM models for Users and Todos tables.
"""

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    """
    SQLAlchemy model for the users table.
    """

    __tablename__: str = "users"

    id: Column = Column(Integer, primary_key=True, index=True)
    email: Column = Column(String, unique=True)
    username: Column = Column(String, unique=True)
    first_name: Column = Column(String)
    last_name: Column = Column(String)
    hashed_password: Column = Column(String)
    is_active: Column = Column(Boolean, default=True)
    role: Column = Column(String)
    phone_number: Column = Column(String)


class Todos(Base):
    """
    SQLAlchemy model for the todos table.
    """

    __tablename__: str = "todos"

    id: Column = Column(Integer, primary_key=True, index=True)
    title: Column = Column(String)
    description: Column = Column(String)
    priority: Column = Column(Integer)
    complete: Column = Column(Boolean, default=False)
    owner_id: Column = Column(Integer, ForeignKey("users.id"))
