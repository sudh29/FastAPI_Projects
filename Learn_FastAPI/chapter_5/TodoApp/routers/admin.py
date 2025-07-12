"""
Admin-related API endpoints for the FastAPI application in Chapter 5.

Includes routes for admin users to view and delete all todos.
"""

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user
from pydantic import ConfigDict
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    complete: bool
    owner_id: int
    model_config = ConfigDict(from_attributes=True)


def get_db() -> Session:
    """
    Dependency that provides a database session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", response_model=list[TodoResponse], status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency) -> list:
    """
    Retrieve all todo items. Only accessible by admin users.
    """
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
) -> None:
    """
    Delete a todo item by ID. Only accessible by admin users.
    """
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
