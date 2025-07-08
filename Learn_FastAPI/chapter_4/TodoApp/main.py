"""
Main entry point for the FastAPI application in Chapter 4.

This module sets up the FastAPI app, initializes the database tables, and includes routers for authentication, todos, admin, and users.
"""

from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    """
    Health check endpoint.

    Returns a JSON response indicating the service status.
    """
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
