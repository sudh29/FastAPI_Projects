"""
Test for the health check endpoint of the FastAPI application.
"""

from fastapi.testclient import TestClient
from ..main import app
from fastapi import status

client = TestClient(app)


def test_return_health_check() -> None:
    """Test that the /healthy endpoint returns status 200 and correct JSON."""
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Healthy"}
