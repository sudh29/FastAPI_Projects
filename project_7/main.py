from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, conint, confloat
from typing import Dict, List, Optional, Tuple
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets
import logging
import asyncio
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Project 7 - Improved Inventory Service")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Basic auth
security = HTTPBasic()
USERNAME = os.getenv("API_USER", "admin")
PASSWORD = os.getenv("API_PASS", "admin")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if not (
        secrets.compare_digest(credentials.username, USERNAME)
        and secrets.compare_digest(credentials.password, PASSWORD)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


# Models
class ProductIn(BaseModel):
    id: int
    name: str
    price: confloat(ge=0)
    description: Optional[str] = None
    quantity: conint(ge=0)


class Product(ProductIn):
    version: int = Field(0, description="Optimistic lock revision")


class InventoryUpdate(BaseModel):
    delta: int


class ErrorResponse(BaseModel):
    detail: str


# In-memory storage and locks (swap for async DB/Redis in prod)
_db: Dict[int, Product] = {}
_locks: Dict[int, asyncio.Lock] = {}

# Cache for low-stock alerts
_alerts_cache: Dict[int, Tuple[float, List[Product]]] = {}
_CACHE_TTL = 5.0


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return PlainTextResponse(
        "Rate limit exceeded", status_code=status.HTTP_429_TOO_MANY_REQUESTS
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# CRUD Endpoints
@limiter.limit("10/minute")
@app.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
async def create_product(
    request: Request, product_in: ProductIn, credentials=Depends(authenticate)
):
    lock = _locks.setdefault(product_in.id, asyncio.Lock())
    async with lock:
        if product_in.id in _db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product ID already exists.",
            )
        prod = Product(**product_in.dict())
        _db[prod.id] = prod
        return prod


@limiter.limit("20/minute")
@app.get(
    "/products/{product_id}",
    response_model=Product,
    responses={404: {"model": ErrorResponse}},
)
async def get_product(
    request: Request, product_id: int, credentials=Depends(authenticate)
):
    prod = _db.get(product_id)
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )
    return prod


@limiter.limit("20/minute")
@app.patch(
    "/products/{product_id}/inventory",
    response_model=Product,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
async def update_inventory(
    request: Request,
    product_id: int,
    update: InventoryUpdate,
    credentials=Depends(authenticate),
):
    prod = _db.get(product_id)
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )
    lock = _locks.setdefault(product_id, asyncio.Lock())
    async with lock:
        new_qty = prod.quantity + update.delta
        if new_qty < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock."
            )
        prod.quantity = new_qty
        prod.version += 1
    return prod


@limiter.limit("20/minute")
@app.get("/products/alerts", response_model=List[Product])
async def low_stock_alerts(
    request: Request, threshold: int = 10, credentials=Depends(authenticate)
):
    now = time.monotonic()
    ts, data = _alerts_cache.get(threshold, (0.0, []))
    if now - ts < _CACHE_TTL:
        return data
    result = [p for p in _db.values() if p.quantity <= threshold]
    _alerts_cache[threshold] = (now, result)
    return result


@limiter.limit("10/minute")
@app.get("/products", response_model=List[Product])
async def list_products(request: Request, credentials=Depends(authenticate)):
    # No lock needed for read-only
    return list(_db.values())


# Added DELETE endpoint to maintain feature parity with old main.py
@limiter.limit("5/minute")
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    request: Request,
    product_id: int,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    lock = _locks.setdefault(product_id, asyncio.Lock())
    async with lock:
        if product_id in _db:
            del _db[product_id]
            # Clean up lock if possible, but it's tricky with async locks in use.
            # For simple in-memory, leaving it is fine or use a more complex manager.
            return
        raise HTTPException(status_code=404, detail="Product not found")


# Added PUT endpoint to maintain feature parity with old main.py
@limiter.limit("5/minute")
@app.put(
    "/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK
)
async def update_product(
    request: Request,
    product_id: int,
    product_in: ProductIn,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    lock = _locks.setdefault(product_id, asyncio.Lock())
    async with lock:
        if product_id in _db:
            # Update fields
            prod = _db[product_id]
            prod.name = product_in.name
            prod.price = product_in.price
            prod.description = product_in.description
            prod.quantity = product_in.quantity
            prod.version += 1
            return prod
        raise HTTPException(status_code=404, detail="Product not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
