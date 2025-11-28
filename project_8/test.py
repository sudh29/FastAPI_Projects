import asyncio
import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, ASGITransport
from main import (
    app,
    manager,
    Product,
    lifespan,
)
from datetime import datetime, timezone


@pytest_asyncio.fixture(autouse=True)
async def init_inventory():
    # Clear all state
    manager._inventory.clear()
    manager._rate_limits.clear()
    manager._cache.clear()
    manager._circuit.clear()
    manager._subscribers.clear()

    # Run lifespan to seed data
    async with lifespan(app):
        yield


@pytest.mark.asyncio
async def test_get_product_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/products/test1", headers={"X-Client-Id": "user1"})
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        assert data["id"] == "test1"
        assert data["quantity"] == 15


@pytest.mark.asyncio
async def test_get_product_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/products/unknown", headers={"X-Client-Id": "user1"})
        assert r.status_code == status.HTTP_404_NOT_FOUND
        assert r.json()["detail"] == "Product not found"


@pytest.mark.asyncio
async def test_update_product_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"operation": "add", "quantity": 5}
        r = await ac.put(
            "/products/test1?version=1", json=payload, headers={"X-Client-Id": "user1"}
        )
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        assert data["quantity"] == 20
        assert data["version"] == 2


@pytest.mark.asyncio
async def test_update_product_version_mismatch():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"operation": "add", "quantity": 1}
        r = await ac.put(
            "/products/test1?version=99", json=payload, headers={"X-Client-Id": "user1"}
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Version mismatch" in r.json()["detail"]


@pytest.mark.asyncio
async def test_concurrent_updates():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        tasks = [
            ac.put(
                "/products/test1?version=1",
                json={"operation": "add", "quantity": 1},
                headers={"X-Client-Id": "user1"},
            )
            for _ in range(10)
        ]
        results = await asyncio.gather(*tasks)
        successes = [r for r in results if r.status_code == 200]
        failures = [r for r in results if r.status_code != 200]
        assert len(successes) == 1
        assert len(failures) == 9


@pytest.mark.asyncio
async def test_rate_limiting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Limit is 100 in main.py now
        for _ in range(100):
            r = await ac.get("/products/test1", headers={"X-Client-Id": "rl_user"})
            assert r.status_code == status.HTTP_200_OK
        r = await ac.get("/products/test1", headers={"X-Client-Id": "rl_user"})
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_bulk_update():
    transport = ASGITransport(app=app)
    # Overwrite test2 for this test
    manager._inventory["test2"] = Product(
        id="test2",
        name="P2",
        quantity=5,
        reserved=0,
        category="books",
        last_updated=datetime.now(timezone.utc),
        version=1,
        supplier_ids=["sup2"],
        min_quantity=1,
        max_quantity=10,
    )
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        req = {
            "updates": [
                {
                    "product_id": "test1",
                    "update": {"operation": "add", "quantity": 2},
                    "version": 1,
                },
                {
                    "product_id": "test2",
                    "update": {"operation": "subtract", "quantity": 3},
                    "version": 1,
                },
            ]
        }
        r = await ac.post("/products/bulk", json=req, headers={"X-Client-Id": "user1"})
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        assert data["test1"]["quantity"] == 17  # 15 + 2
        assert data["test2"]["quantity"] == 2  # 5 - 3


@pytest.mark.asyncio
async def test_webhook_supplier_update():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        prod = manager._inventory["test1"]
        assert prod.reserved == 2  # Initial is 2
        r = await ac.post(
            "/webhook/supplier",
            json={"supplier_id": "sup1", "product_id": "test1", "quantity": 3},
        )
        assert r.status_code == status.HTTP_200_OK
        await asyncio.sleep(0.1)
        prod = manager._inventory["test1"]
        assert prod.reserved == 5  # 2 + 3


@pytest.mark.asyncio
async def test_create_product():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "id": "new_prod",
            "name": "New Gadget",
            "quantity": 100,
            "category": "electronics",
            "min_quantity": 5,
        }
        r = await ac.post("/products", json=payload, headers={"X-Client-Id": "user1"})
        assert r.status_code == status.HTTP_201_CREATED
        data = r.json()
        assert data["id"] == "new_prod"
        assert data["quantity"] == 100

        # Verify it's in the list
        r_list = await ac.get("/products", headers={"X-Client-Id": "user1"})
        assert r_list.status_code == 200
        ids = [p["id"] for p in r_list.json()]
        assert "new_prod" in ids


@pytest.mark.asyncio
async def test_delete_product():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Delete existing product
        r = await ac.delete("/products/test1", headers={"X-Client-Id": "user1"})
        assert r.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        r_get = await ac.get("/products/test1", headers={"X-Client-Id": "user1"})
        assert r_get.status_code == status.HTTP_404_NOT_FOUND

        # Try deleting non-existent
        r_fail = await ac.delete("/products/unknown", headers={"X-Client-Id": "user1"})
        assert r_fail.status_code == status.HTTP_404_NOT_FOUND
