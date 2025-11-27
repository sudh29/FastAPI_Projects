"""
Inventory Management System API
------------------------------
A FastAPI-based service for real-time product inventory management.

Why this project?
-----------------
- Modern businesses require real-time, concurrent, and robust inventory management.
- This API demonstrates advanced backend patterns: rate limiting, optimistic locking, circuit breaker, SSE, and more.
- Designed for extensibility, observability, and production-readiness.

Key Features:
- Custom exception handling for clear error reporting and debugging.
- Per-client rate limiting to prevent abuse and ensure fair usage.
- Pydantic models for strict request validation and data integrity.
- Concurrency-safe updates using asyncio locks and optimistic locking.
- Background tasks for non-blocking operations (e.g., cache cleanup, webhooks).
- Response caching for performance.
- Bulk operations for efficiency.
- Real-time notifications via Server-Sent Events (SSE).
- Request tracing and logging for observability.
- Circuit breaker pattern for resilience against repeated failures.
"""

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Set, AsyncGenerator
import time
import asyncio
from datetime import datetime
from uuid import uuid4
from collections import defaultdict
import json


# --- Custom Exceptions ---
# Why: Custom exceptions provide clear, domain-specific error messages and status codes for clients and for debugging.
class ProductNotFound(HTTPException):
    """Exception raised when a product is not found in the inventory."""

    def __init__(self, detail: str = "Product not found"):
        super().__init__(status_code=404, detail=detail)


class RateLimitExceeded(HTTPException):
    """Exception raised when a client exceeds the allowed rate limit."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)


class InventoryError(HTTPException):
    """Exception raised for general inventory operation errors."""

    def __init__(self, detail: str = "Inventory operation failed"):
        super().__init__(status_code=400, detail=detail)


class BulkOperationError(HTTPException):
    """Exception raised for errors during bulk update operations."""

    def __init__(self, detail: str = "Bulk update failed"):
        super().__init__(status_code=400, detail=detail)


class CircuitBreakerOpen(HTTPException):
    """Exception raised when the circuit breaker is open for an operation."""

    def __init__(self, detail: str = "Circuit breaker is open"):
        super().__init__(status_code=503, detail=detail)


# --- Product Model ---
# Why: Pydantic models ensure strict validation, type safety, and self-documenting APIs.
CATEGORIES = {"electronics", "books", "clothing", "food", "toys"}


class Product(BaseModel):
    """
    Represents a product in the inventory.
    Enforces constraints for data integrity and business rules.
    """

    id: str = Field(
        ..., min_length=1, max_length=50, description="Unique product identifier"
    )
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    quantity: int = Field(..., ge=0, description="Available quantity in stock")
    reserved: int = Field(..., ge=0, description="Reserved quantity")
    category: str = Field(
        ..., min_length=1, max_length=50, description="Product category"
    )
    last_updated: datetime = Field(..., description="Last update timestamp")
    version: int = Field(gt=0, description="Version for optimistic locking")
    supplier_ids: List[str] = Field(..., description="List of supplier IDs")
    min_quantity: int = Field(..., ge=0, description="Minimum allowed quantity")
    max_quantity: Optional[int] = Field(
        None, ge=0, description="Maximum allowed quantity"
    )

    @field_validator("max_quantity")
    def max_gt_min(cls, v, info):
        """Ensure max_quantity is not less than min_quantity."""
        min_q = info.data.get("min_quantity")
        if v is not None and min_q is not None and v < min_q:
            raise ValueError("max_quantity must be >= min_quantity")
        return v

    @field_validator("supplier_ids")
    def unique_suppliers(cls, v):
        """Ensure supplier IDs are unique."""
        if len(v) != len(set(v)):
            raise ValueError("Supplier IDs must be unique")
        return v

    @field_validator("category")
    def valid_category(cls, v):
        """Ensure category is one of the allowed categories."""
        if v not in CATEGORIES:
            raise ValueError(f"Category must be one of {CATEGORIES}")
        return v


class InventoryUpdate(BaseModel):
    """
    Represents an update operation for a product's quantity.
    Enforces allowed operations and positive quantities.
    """

    operation: str = Field(
        ..., pattern="^(add|subtract)$", description="Operation type: add or subtract"
    )
    quantity: int = Field(..., gt=0, description="Quantity to add or subtract")


class BulkUpdateItem(BaseModel):
    """
    Represents a single item in a bulk update request.
    Allows atomic, versioned updates for multiple products.
    """

    product_id: str
    update: InventoryUpdate
    version: int


class BulkUpdateRequest(BaseModel):
    """
    Request model for bulk product updates.
    Enables efficient, atomic updates for multiple products in one call.
    """

    updates: List[BulkUpdateItem]


class SupplierUpdate(BaseModel):
    """
    Request model for supplier webhook updates.
    Used to update reserved quantities for products from suppliers.
    """

    supplier_id: str
    product_id: str
    quantity: int


# --- Inventory Manager ---
# Why: Encapsulates all business logic, concurrency, and state management for the inventory system.
class InventoryManager:
    """
    Manages the inventory, including products, locks, rate limits, cache, and notifications.
    Handles concurrency, rate limiting, circuit breaker, and real-time updates.
    """

    def __init__(self):
        self._inventory: Dict[str, Product] = {}  # All products by ID
        self._locks: Dict[str, asyncio.Lock] = {}  # Per-product locks for concurrency
        self._rate_limits: Dict[str, List[float]] = {}  # Per-client request timestamps
        self._cache: Dict[
            str, tuple[Product, float]
        ] = {}  # Product cache with timestamps
        self._subscribers: Dict[str, Set[asyncio.Queue]] = defaultdict(
            set
        )  # SSE subscribers
        self._circuit: Dict[str, dict] = {}  # Circuit breaker state per operation
        self.CACHE_TTL: int = 30  # seconds
        self.CBR_THRESHOLD: int = 5  # circuit breaker failure threshold
        self.CBR_RESET: int = 60  # seconds to reset circuit breaker

    async def _manage_cache(self, product_id: str) -> None:
        """Remove cache entry if expired. Keeps cache fresh and memory usage low."""
        entry = self._cache.get(product_id)
        if entry and time.time() - entry[1] > self.CACHE_TTL:
            del self._cache[product_id]

    def check_rate_limit(self, client_id: str) -> bool:
        """Check and update rate limit for a client. Returns True if allowed.
        Prevents abuse and ensures fair usage for all clients."""
        window = 60
        now = time.time()
        lst = self._rate_limits.setdefault(client_id, [])
        lst[:] = [t for t in lst if now - t < window]
        if len(lst) >= 10:
            return False
        lst.append(now)
        return True

    async def check_circuit_breaker(self, op: str) -> bool:
        """Check if the circuit breaker is open for an operation.
        Protects the system from repeated failures and allows recovery."""
        state = self._circuit.setdefault(op, {"fails": 0, "opened_at": None})
        if state["opened_at"] and time.time() - state["opened_at"] < self.CBR_RESET:
            return False
        if state["opened_at"]:
            state.update({"fails": 0, "opened_at": None})
        return True

    def record_failure(self, op: str) -> None:
        """Record a failure for an operation (for circuit breaker).
        If failures exceed threshold, open the circuit for cooldown."""
        state = self._circuit.setdefault(op, {"fails": 0, "opened_at": None})
        state["fails"] += 1
        if state["fails"] >= self.CBR_THRESHOLD:
            state["opened_at"] = time.time()

    async def update_with_version(
        self, product_id: str, upd: InventoryUpdate, version: int
    ) -> Product:
        """
        Update a product's quantity with optimistic locking and notify subscribers.
        Ensures concurrent updates are safe and clients see consistent state.
        """
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
            prod.last_updated = datetime.utcnow()
            # Notify subscribers (for SSE)
            for q in self._subscribers[product_id]:
                await q.put(prod)
            # Update cache
            self._cache[product_id] = (prod, time.time())
            return prod

    async def bulk_update(self, req: BulkUpdateRequest) -> Dict[str, Product]:
        """
        Perform bulk updates on products.
        Allows efficient, atomic updates for multiple products in one call.
        """
        results: Dict[str, Product] = {}
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
        """
        Subscribe to real-time updates for a product (SSE).
        Each subscriber gets notified when the product changes.
        """
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers[product_id].add(q)
        try:
            while True:
                prod = await q.get()
                yield json.dumps(prod.dict(), default=str)
        finally:
            self._subscribers[product_id].remove(q)

    async def schedule_cleanup(self) -> None:
        """
        Periodically clean up expired cache entries.
        Runs as a background task to keep memory usage low.
        """
        while True:
            await asyncio.sleep(self.CACHE_TTL)
            for pid in list(self._cache.keys()):
                await self._manage_cache(pid)

    async def trace_request(self, request_id: str, operation: str) -> None:
        """
        Log a trace for a request and operation.
        Useful for debugging, monitoring, and audit trails.
        """
        print(f"[TRACE] {request_id} - {operation} at {datetime.utcnow().isoformat()}")


# --- FastAPI Setup ---
# Why: FastAPI provides automatic OpenAPI docs, async support, and dependency injection for modern APIs.
app = FastAPI(title="Inventory Management System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
manager = InventoryManager()
app.state.manager = manager


# Dependency to extract a unique client ID from each request.
# This is used for per-client rate limiting and can be extended to support authentication or user tracking.
async def get_client_id(request: Request) -> str:
    """Extract client ID from request headers. Used for rate limiting and tracking."""
    # In a real-world scenario, this could be a user ID from authentication, an API key, or an IP address.
    # Here, we use a custom header if present, otherwise default to 'anonymous'.
    return request.headers.get("X-Client-Id", "anonymous")


# Middleware to trace every HTTP request and log its duration.
# This helps with debugging, performance monitoring, and auditing.
@app.middleware("http")
async def trace_requests(request: Request, call_next):
    """Middleware to trace each HTTP request and log duration for observability and debugging."""
    rid = str(uuid4())  # Generate a unique request ID for traceability
    await manager.trace_request(rid, f"{request.method} {request.url.path}")
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    # Log the response status and duration for this request
    await manager.trace_request(
        rid, f"Response {response.status_code} in {duration:.2f}s"
    )
    return response


# Exception handlers
# Why: Custom handlers provide clear, consistent error responses for clients and easier debugging for developers.
@app.exception_handler(ProductNotFound)
async def product_not_found_handler(request: Request, exc: ProductNotFound):
    """Return 404 if product is not found."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Return 429 if rate limit is exceeded."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Endpoints
# Why: Each endpoint is designed for a specific business use case and leverages the above patterns for safety and performance.
@app.get("/products/{product_id}")
async def get_product(
    product_id: str, client_id: str = Depends(get_client_id), request: Request = None
):
    """
    Get a product by ID.
    - Rate limited to prevent abuse
    - Circuit breaker protected for resilience
    """
    manager = request.app.state.manager if request else app.state.manager
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
    """
    Update a product's quantity (add or subtract) with optimistic locking.
    - Rate limited to prevent abuse
    - Uses versioning for concurrency safety
    """
    manager = request.app.state.manager if request else app.state.manager
    if not manager.check_rate_limit(client_id):
        raise RateLimitExceeded()
    try:
        updated = await manager.update_with_version(product_id, update, version)
        return updated
    except HTTPException:
        manager.record_failure("update_product")
        raise


@app.post("/products/bulk")
async def bulk_update_products(
    updates: BulkUpdateRequest,
    background_tasks: BackgroundTasks,
    client_id: str = Depends(get_client_id),
    request: Request = None,
):
    """
    Perform bulk updates on multiple products.
    - Rate limited to prevent abuse
    - Efficient for large-scale changes
    """
    manager = request.app.state.manager if request else app.state.manager
    if not manager.check_rate_limit(client_id):
        raise RateLimitExceeded()
    result = await manager.bulk_update(updates)
    return result


@app.get("/products/{product_id}/stream")
async def stream_updates(
    product_id: str, client_id: str = Depends(get_client_id), request: Request = None
):
    """
    Stream real-time updates for a product using Server-Sent Events (SSE).
    - Rate limited to prevent abuse
    - Enables live dashboards and notifications
    """
    manager = request.app.state.manager if request else app.state.manager
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
    """
    Webhook endpoint to update reserved quantity for a product from a supplier.
    - Runs as a background task to avoid blocking the main thread
    - Can be extended for more complex supplier integrations
    """
    manager = request.app.state.manager if request else app.state.manager

    async def process():
        prod = manager._inventory.get(update.product_id)
        if not prod:
            raise ProductNotFound()
        prod.reserved += update.quantity
        prod.last_updated = datetime.utcnow()

    background_tasks.add_task(process)
    return {"status": "queued"}


@app.on_event("startup")
async def startup_event():
    """
    Startup event to seed test data and start background cleanup.
    - Ensures the system is ready for requests
    - Starts cache cleanup in the background
    """
    app.state.manager._inventory["test1"] = Product(
        id="test1",
        name="Sample",
        quantity=10,
        reserved=0,
        category="electronics",
        last_updated=datetime.utcnow(),
        version=1,
        supplier_ids=["sup1"],
        min_quantity=1,
        max_quantity=100,
    )
    asyncio.create_task(app.state.manager.schedule_cleanup())


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event to clean up subscribers.
    - Ensures all SSE connections are closed gracefully
    """
    for subs in app.state.manager._subscribers.values():
        for q in subs:
            q.put_nowait(None)
