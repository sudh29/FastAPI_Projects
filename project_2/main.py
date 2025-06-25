# Import necessary FastAPI and Python modules
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

# Initialize FastAPI app
app = FastAPI(title="Project 2")

# Set up basic logging for error tracking
logging.basicConfig(level=logging.INFO)


# Define the Product data model using Pydantic
class Product(BaseModel):
    id: int  # Unique identifier for the product
    name: str  # Name of the product
    price: float  # Price of the product
    description: Optional[str] = None  # Optional description


# In-memory storage for products using a dictionary for O(1) access
# Key: product id, Value: Product object
db: dict[int, Product] = {}
# Async lock to ensure concurrency safety for db operations
db_lock = asyncio.Lock()

# Set up rate limiting using slowapi (limits requests per IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Set up HTTP Basic authentication
security = HTTPBasic()
# Demo credentials (in production, use a secure user store)
USERNAME = "admin"
PASSWORD = "admin"


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Authenticate user using HTTP Basic Auth.
    Raises 401 if credentials are invalid.
    """
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


# Global exception handler for unhandled errors
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Exception handler for validation errors (e.g., invalid request body)
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


# Exception handler for rate limit exceeded
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return PlainTextResponse("Rate limit exceeded", status_code=429)


# Endpoint: Get all products
@app.get("/products", response_model=List[Product], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_all_products(
    request: Request, credentials: HTTPBasicCredentials = Depends(authenticate)
):
    """
    Returns a list of all products in the database.
    Requires authentication and is rate limited.
    """
    async with db_lock:
        return list(db.values())


# Endpoint: Get a single product by ID
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
    Returns a single product by its ID.
    Raises 404 if not found. Requires authentication and is rate limited.
    """
    async with db_lock:
        product = db.get(product_id)
        if product:
            return product
        raise HTTPException(status_code=404, detail="Product not found")


# Endpoint: Create a new product
@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_product(
    request: Request,
    product: Product,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    """
    Creates a new product. Product ID must be unique.
    Raises 400 if product with the same ID exists.
    Requires authentication and is rate limited.
    """
    async with db_lock:
        if product.id in db:
            raise HTTPException(
                status_code=400, detail="Product with this ID already exists"
            )
        db[product.id] = product
        return product


# Endpoint: Update an existing product
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
    Updates an existing product by ID.
    Raises 404 if product not found. Requires authentication and is rate limited.
    """
    async with db_lock:
        if product_id in db:
            db[product_id] = product
            return product
        raise HTTPException(status_code=404, detail="Product not found")


# Endpoint: Delete a product by ID
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_product(
    request: Request,
    product_id: int,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    """
    Deletes a product by its ID.
    Raises 404 if product not found. Requires authentication and is rate limited.
    """
    async with db_lock:
        if product_id in db:
            del db[product_id]
            return
        raise HTTPException(status_code=404, detail="Product not found")
