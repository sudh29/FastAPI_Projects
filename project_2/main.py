from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import logging
import asyncio

app = FastAPI(title="Project 2")

# Set up basic logging
logging.basicConfig(level=logging.INFO)


class Product(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None


# In-memory storage for products (use dict for O(1) access)
db: dict[int, Product] = {}
db_lock = asyncio.Lock()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

security = HTTPBasic()

# Simple user store (for demo purposes)
USERNAME = "admin"
PASSWORD = "admin"


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return PlainTextResponse("Rate limit exceeded", status_code=429)


@app.get("/products", response_model=List[Product], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_all_products(
    request: Request, credentials: HTTPBasicCredentials = Depends(authenticate)
):
    """
    Get all products
    """
    async with db_lock:
        return list(db.values())


@app.get(
    "/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK
)
@limiter.limit("5/minute")
async def get_one_product(
    request: Request,
    product_id: int,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    """
    Get one product
    """
    async with db_lock:
        product = db.get(product_id)
        if product:
            return product
        raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_product(
    request: Request,
    product: Product,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    """
    Create a new product
    """
    async with db_lock:
        if product.id in db:
            raise HTTPException(
                status_code=400, detail="Product with this ID already exists"
            )
        db[product.id] = product
        return product


@app.put(
    "/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK
)
@limiter.limit("5/minute")
async def update_product(
    request: Request,
    product_id: int,
    product: Product,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    """
    Update a product
    """
    async with db_lock:
        if product_id in db:
            db[product_id] = product
            return product
        raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_product(
    request: Request,
    product_id: int,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    """
    Delete a product
    """
    async with db_lock:
        if product_id in db:
            del db[product_id]
            return
        raise HTTPException(status_code=404, detail="Product not found")
