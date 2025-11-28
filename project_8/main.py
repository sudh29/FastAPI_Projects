"""
Inventory Management System API
------------------------------
A FastAPI-based service for real-time product inventory management.
Includes a GUI dashboard.
"""

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks, status
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Set, AsyncGenerator
import time
import asyncio
from datetime import datetime, timezone
from uuid import uuid4
from collections import defaultdict
import json
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Custom Exceptions ---
class ProductNotFound(HTTPException):
    def __init__(self, detail: str = "Product not found"):
        super().__init__(status_code=404, detail=detail)


class RateLimitExceeded(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)


class InventoryError(HTTPException):
    def __init__(self, detail: str = "Inventory operation failed"):
        super().__init__(status_code=400, detail=detail)


class BulkOperationError(HTTPException):
    def __init__(self, detail: str = "Bulk update failed"):
        super().__init__(status_code=400, detail=detail)


class CircuitBreakerOpen(HTTPException):
    def __init__(self, detail: str = "Circuit breaker is open"):
        super().__init__(status_code=503, detail=detail)


# --- Models ---
CATEGORIES = {"electronics", "books", "clothing", "food", "toys", "Random"}


class Product(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    reserved: int = Field(..., ge=0)
    category: str
    last_updated: datetime
    version: int = Field(gt=0)
    supplier_ids: List[str]
    min_quantity: int = Field(..., ge=0)
    max_quantity: Optional[int] = Field(None, ge=0)

    @field_validator("max_quantity")
    def max_gt_min(cls, v, info):
        min_q = info.data.get("min_quantity")
        if v is not None and min_q is not None and v < min_q:
            raise ValueError("max_quantity must be >= min_quantity")
        return v

    @field_validator("supplier_ids")
    def unique_suppliers(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Supplier IDs must be unique")
        return v

    @field_validator("category")
    def valid_category(cls, v):
        if v not in CATEGORIES:
            raise ValueError(f"Category must be one of {CATEGORIES}")
        return v


class InventoryUpdate(BaseModel):
    operation: str = Field(..., pattern="^(add|subtract)$")
    quantity: int = Field(..., gt=0)


class BulkUpdateItem(BaseModel):
    product_id: str
    update: InventoryUpdate
    version: int


class BulkUpdateRequest(BaseModel):
    updates: List[BulkUpdateItem]


class SupplierUpdate(BaseModel):
    supplier_id: str
    product_id: str
    quantity: int


class ProductCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    category: str
    min_quantity: int = Field(0, ge=0)
    max_quantity: Optional[int] = Field(None, ge=0)


# --- Inventory Manager ---
class InventoryManager:
    def __init__(self):
        self._inventory: Dict[str, Product] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._rate_limits: Dict[str, List[float]] = {}
        self._cache: Dict[str, tuple[Product, float]] = {}
        self._subscribers: Dict[str, Set[asyncio.Queue]] = defaultdict(set)
        self._circuit: Dict[str, dict] = {}
        self.CACHE_TTL = 30
        self.CBR_THRESHOLD = 5
        self.CBR_RESET = 60

    async def _manage_cache(self, product_id: str) -> None:
        entry = self._cache.get(product_id)
        if entry and time.time() - entry[1] > self.CACHE_TTL:
            del self._cache[product_id]

    def check_rate_limit(self, client_id: str) -> bool:
        window = 60
        now = time.time()
        lst = self._rate_limits.setdefault(client_id, [])
        lst[:] = [t for t in lst if now - t < window]
        if len(lst) >= 100:
            return False
        lst.append(now)
        return True

    async def check_circuit_breaker(self, op: str) -> bool:
        state = self._circuit.setdefault(op, {"fails": 0, "opened_at": None})
        if state["opened_at"] and time.time() - state["opened_at"] < self.CBR_RESET:
            return False
        if state["opened_at"]:
            state.update({"fails": 0, "opened_at": None})
        return True

    def record_failure(self, op: str) -> None:
        state = self._circuit.setdefault(op, {"fails": 0, "opened_at": None})
        state["fails"] += 1
        if state["fails"] >= self.CBR_THRESHOLD:
            state["opened_at"] = time.time()

    async def update_with_version(
        self, product_id: str, upd: InventoryUpdate, version: int
    ) -> Product:
        lock = self._locks.setdefault(product_id, asyncio.Lock())
        async with lock:
            prod = self._inventory.get(product_id)
            if not prod:
                raise ProductNotFound()
            if prod.version != version:
                raise InventoryError("Version mismatch")

            if upd.operation == "add":
                prod.quantity += upd.quantity
            else:
                if prod.quantity < upd.quantity:
                    raise InventoryError("Insufficient stock")
                prod.quantity -= upd.quantity

            prod.version += 1
            prod.last_updated = datetime.now(timezone.utc)

            # Notify subscribers
            for q in self._subscribers[product_id]:
                await q.put(prod)

            self._cache[product_id] = (prod, time.time())
            return prod

    async def bulk_update(self, req: BulkUpdateRequest) -> Dict[str, Product]:
        results = {}
        for item in req.updates:
            try:
                updated = await self.update_with_version(
                    item.product_id, item.update, item.version
                )
                results[item.product_id] = updated
            except Exception as e:
                raise BulkOperationError(f"Failed {item.product_id}: {e}")
        return results

    async def subscribe_to_updates(self, product_id: str) -> AsyncGenerator[str, None]:
        q = asyncio.Queue()
        self._subscribers[product_id].add(q)
        try:
            while True:
                prod = await q.get()
                yield json.dumps(prod.dict(), default=str)
        finally:
            self._subscribers[product_id].remove(q)

    async def schedule_cleanup(self) -> None:
        while True:
            await asyncio.sleep(self.CACHE_TTL)
            for pid in list(self._cache.keys()):
                await self._manage_cache(pid)

    async def trace_request(self, request_id: str, operation: str) -> None:
        logger.info(f"[TRACE] {request_id} - {operation}")


# --- Application Setup ---

# Initialize Manager Global
manager = InventoryManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.manager._inventory["test1"] = Product(
        id="test1",
        name="Gaming Laptop",
        quantity=15,
        reserved=2,
        category="electronics",
        last_updated=datetime.now(timezone.utc),
        version=1,
        supplier_ids=["sup1"],
        min_quantity=5,
        max_quantity=100,
    )
    app.state.manager._inventory["test2"] = Product(
        id="test2",
        name="Cotton T-Shirt",
        quantity=50,
        reserved=0,
        category="clothing",
        last_updated=datetime.now(timezone.utc),
        version=1,
        supplier_ids=["sup2"],
        min_quantity=10,
        max_quantity=200,
    )
    cleanup_task = asyncio.create_task(app.state.manager.schedule_cleanup())

    yield

    # Shutdown
    cleanup_task.cancel()
    for subs in app.state.manager._subscribers.values():
        for q in subs:
            q.put_nowait(None)


app = FastAPI(title="Inventory Management System", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.manager = manager


async def get_client_id(request: Request) -> str:
    return request.headers.get("X-Client-Id", "anonymous")


@app.middleware("http")
async def trace_requests(request: Request, call_next):
    rid = str(uuid4())
    await manager.trace_request(rid, f"{request.method} {request.url.path}")
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    await manager.trace_request(
        rid, f"Response {response.status_code} in {duration:.2f}s"
    )
    return response


# --- Endpoints ---


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/products", response_model=List[Product])
async def list_products(request: Request):
    """List all products (for GUI)."""
    return list(request.app.state.manager._inventory.values())


@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    client_id: str = Depends(get_client_id),
    request: Request = None,
):
    manager = request.app.state.manager
    if not manager.check_rate_limit(client_id):
        raise RateLimitExceeded()

    if product.id in manager._inventory:
        raise HTTPException(status_code=400, detail="Product already exists")

    new_product = Product(
        id=product.id,
        name=product.name,
        quantity=product.quantity,
        reserved=0,
        category=product.category,
        last_updated=datetime.now(timezone.utc),
        version=1,
        supplier_ids=[],
        min_quantity=product.min_quantity,
        max_quantity=product.max_quantity,
    )

    manager._inventory[product.id] = new_product
    return new_product


@app.get("/products/{product_id}")
async def get_product(
    product_id: str, client_id: str = Depends(get_client_id), request: Request = None
):
    manager = request.app.state.manager
    if not manager.check_rate_limit(client_id):
        raise RateLimitExceeded()
    if not await manager.check_circuit_breaker("get_product"):
        raise CircuitBreakerOpen()

    prod = manager._inventory.get(product_id)
    if not prod:
        raise ProductNotFound()
    return prod


@app.put("/products/{product_id}")
async def update_product(
    product_id: str,
    update: InventoryUpdate,
    version: int,
    client_id: str = Depends(get_client_id),
    request: Request = None,
):
    manager = request.app.state.manager
    if not manager.check_rate_limit(client_id):
        raise RateLimitExceeded()
    try:
        return await manager.update_with_version(product_id, update, version)
    except HTTPException:
        manager.record_failure("update_product")
        raise


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str, client_id: str = Depends(get_client_id), request: Request = None
):
    manager = request.app.state.manager
    if not manager.check_rate_limit(client_id):
        raise RateLimitExceeded()

    async with manager._locks.setdefault(product_id, asyncio.Lock()):
        if product_id not in manager._inventory:
            raise ProductNotFound()
        del manager._inventory[product_id]
        if product_id in manager._cache:
            del manager._cache[product_id]


@app.post("/products/bulk")
async def bulk_update_products(
    updates: BulkUpdateRequest,
    client_id: str = Depends(get_client_id),
    request: Request = None,
):
    manager = request.app.state.manager
    if not manager.check_rate_limit(client_id):
        raise RateLimitExceeded()
    return await manager.bulk_update(updates)


@app.get("/products/{product_id}/stream")
async def stream_updates(
    product_id: str, client_id: str = Depends(get_client_id), request: Request = None
):
    manager = request.app.state.manager
    if not manager.check_rate_limit(client_id):
        raise RateLimitExceeded()

    async def event_generator():
        async for data in manager.subscribe_to_updates(product_id):
            yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/webhook/supplier")
async def supplier_webhook(
    update: SupplierUpdate, background_tasks: BackgroundTasks, request: Request = None
):
    manager = request.app.state.manager

    async def process():
        prod = manager._inventory.get(update.product_id)
        if prod:
            prod.reserved += update.quantity
            prod.last_updated = datetime.now(timezone.utc)

    background_tasks.add_task(process)
    return {"status": "queued"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
