# """
# Senior Python Developer Challenge
# Time: 60 minutes

# Create a FastAPI service for a real-time product inventory system.
# Focus on error handling, concurrency, and performance optimization.

# Requirements:
# - Custom exception handling  -  Done
# - Rate limiting per client - Done
# - Request validation - Done
# - Concurrent update handling
# - Background tasks
# - Response caching
# - Bulk operations
# - Real-time notifications
# - Request tracing
# - Circuit breaker pattern
# """

# from fastapi import FastAPI, HTTPException, Request, Depends, status, BackgroundTasks
# from fastapi.responses import JSONResponse, StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, constr, conint, validator
# from typing import Dict, List, Optional, Set, AsyncGenerator
# import time
# import asyncio
# from datetime import datetime
# import uvicorn
# import json
# from enum import Enum
# from collections import defaultdict
# import logging
# from slowapi import Limiter
# from slowapi.util import get_remote_address

# logging.basicConfig(level=logging.INFO)

# # TODO 1: Implement these custom exceptions
# class ProductNotFound(HTTPException):
#     raise HTTPException(status_code=500,details="Product is not present")

# class RateLimitExceeded(HTTPException):
#     raise HTTPException(status_code=429,details="RateLimitExceeded")

# class InventoryError(HTTPException):
#     raise HTTPException(status_code=500,details="InventoryError")

# class BulkOperationError(HTTPException):
#     raise HTTPException(status_code=500,details="BulkOperationError")

# class CircuitBreakerOpen(HTTPException):
#     raise HTTPException(status_code=500,details="CircuitBreakerOpen")

# # TODO 2: Enhance the Product model with more validation rules
# class Product(BaseModel):
#     id: constr(min_length=1, max_length=50)
#     name: constr(min_length=1, max_length=100)
#     quantity: conint(ge=0)
#     reserved: conint(ge=0)
#     category: Enum(['Electronics','Clothing','Random'])
#     last_updated: datetime
#     version: conint(ge=1)  # for optimistic locking
#     supplier_ids: set[str]
#     min_quantity: conint(ge=0)
#     max_quantity: Optional[conint(ge=min_quantity+1)]

#     # TODO 3: Implement validators for:
#     # - version must be positive -- Done
#     # - max_quantity must be greater than min_quantity if set -- Done
#     # - supplier_ids must be unique -- Done
#     # - category must be from predefined list -- Done

# # TODO 4: Implement request models
# class InventoryUpdate(BaseModel):
#     id: constr(min_length=1, max_length=50)
#     name: constr(min_length=1, max_length=100)
#     quantity: conint(ge=0)
#     reserved: conint(ge=0)
#     category: Enum(['Electronics','Clothing','Random'])
#     last_updated: datetime
#     version: conint(ge=1)  # for optimistic locking
#     supplier_ids: set[str]
#     min_quantity: conint(ge=0)
#     max_quantity: Optional[conint(ge=min_quantity+1)]

# class BulkUpdateRequest(BaseModel):
#     products : List[Product]
#     version: List[conint(ge=1)]  # for optimistic locking


# class SupplierUpdate(BaseModel):
#     supplier_ids: set[str]

# # TODO 5: Implement the InventoryManager
# class InventoryManager:
#     def __init__(self):
#         self._inventory: Dict[str, Product] = {}
#         self._locks: Dict[str, asyncio.Lock] = {}
#         self._rate_limits: Dict[str, List[float]] = {}
#         self._cache: Dict[str, tuple[Product, float]] = {}
#         self._subscribers: Dict[str, Set[asyncio.Queue]] = defaultdict(set)
#         self._circuit_breakers: Dict[str, dict] = {}
#         self.CACHE_TTL = 30

#     # TODO 6: Implement cache management
#     async def _manage_cache(self, product_id: str) -> None:
#         if product_id not in self._cache.keys():
#             self._cache[product_id] = (self._inventory.get(product_id),1.0)

#     # TODO 7: Implement rate limiting with sliding window
#     def check_rate_limit(self, client_id: str) -> bool:
#         if client_id not in self._rate_limits:
#             self._rate_limits[client_id] = []

#     # TODO 8: Implement circuit breaker pattern
#     async def check_circuit_breaker(self, operation: str) -> bool:
#         pass

#     # TODO 9: Implement optimistic locking
#     async def update_with_version(self, product_id: str, update: InventoryUpdate, version: int) -> Product:
#         if product_id in self._inventory.keys():
#             self._inventory[product_id].version = version
#             return self._inventory[product_id]

#     # TODO 10: Implement bulk operations
#     async def bulk_update(self, updates: BulkUpdateRequest) -> Dict[str, Product]:
#         res = {}
#         for product, version in zip(updates.products, updates.version):
#             product_id = product.product_id
#             self._inventory[product_id].version = version
#                 res[product_id] = self._inventory[product_id]
#         return res

#     # TODO 11: Implement real-time notification system
#     async def subscribe_to_updates(self, product_id: str) -> AsyncGenerator[Product, None]:
#         if product_id in self._inventory.keys():
#             return AsyncGenerator(self._inventory[product_id], None)

#     # TODO 12: Implement background tasks
#     async def schedule_cleanup(self) -> None:
#         del self._inventory
#         del self._locks
#         del self._rate_limits
#         del self._cache
#         del self._subscribers
#         del self._circuit_breakers

#     # TODO 13: Implement request tracing
#     async def trace_request(self, request_id: str, operation: str) -> None:
#         pass

# # TODO 14: Implement middleware for request tracing
# @app.middleware("http")
# async def trace_requests(request: Request, call_next):
#     self.trace_request(request, call_next)

# # TODO 15: Implement the FastAPI application
# app = FastAPI(title="Inventory Management System")

# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter

# # TODO 16: Implement exception handlers
# @app.exception_handler(ProductNotFound)
# async def product_not_found_handler(request: Request, exc: ProductNotFound):
#     logging.error(f"ProductNotFound error: {exc}")
#     return JSONResponse(status_code=500,content{"details":"Product is not present"})

# # TODO 17: Implement API endpoints
# @app.get("/products/{product_id}")
# @limiter.limit("5/min")
# async def get_product(
#     product_id: str,
#     client_id: str = Depends(get_client_id)
# ):
#     async with IM._locks:
#         if product_id in IM._inventory.keys():
#             return IM._inventory[product_id]
#         raise product_not_found_handler()

# @app.put("/products/{product_id}")
# @limiter.limit("5/min")
# async def update_product(
#     product_id: str,
#     update: InventoryUpdate,
#     version: int,
#     client_id: str = Depends(get_client_id)
# ):
#     async with IM._locks:
#         if product_id in IM._inventory.keys():
#             IM._inventory[product_id] = update
#             IM.update_with_version(product_id, update, version)
#             return IM._inventory[product_id]
#         raise product_not_found_handler()

# # TODO 18: Implement bulk update endpoint
# @app.post("/products/bulk")
# @limiter.limit("5/min")
# async def bulk_update_products(
#     updates: BulkUpdateRequest,
#     background_tasks: BackgroundTasks,
#     client_id: str = Depends(get_client_id)
# ):
#     async with IM._locks:
#         return IM.bulk_update(updates)

# # TODO 19: Implement SSE endpoint for real-time updates
# @app.get("/products/{product_id}/stream")
# @limiter.limit("5/min")
# async def stream_updates(
#     product_id: str,
#     client_id: str = Depends(get_client_id)
# ):
#     pass

# # TODO 20: Implement supplier update webhook
# @app.post("/webhook/supplier")
# @limiter.limit("5/min")
# async def supplier_webhook(
#     update: SupplierUpdate,
#     background_tasks: BackgroundTasks
# ):
#     pass

# @app.on_event("startup")
# async def startup_event():
#     IM = InventoryManager()
#     # - Test data
#     # - Background tasks
#     # - Cleanup routines
#     # - Circuit breaker state


# @app.on_event("shutdown")
# async def shutdown_event():
#     # TODO 22: Implement cleanup:
#     # - Close all subscriptions
#     # - Save state
#     IM.schedule_cleanup()


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# """
# Test cases to implement (TODO 23):

# 1. Basic CRUD operations
# 2. Concurrent updates to same product
# 3. Rate limiting functionality
# 4. Cache invalidation
# 5. Error handling scenarios
# 6. Race conditions
# 7. Bulk update operations
# 8. Real-time notifications
# 9. Circuit breaker functionality
# 10. Request tracing
# 11. Background task execution
# 12. Webhook handling
# 13. Performance under load
# 14. Data consistency checks
# 15. Optimistic locking scenarios

# Example test:
# ```python
# import asyncio
# import aiohttp
# import pytest

# async def test_concurrent_updates():
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for _ in range(10):
#             tasks.append(asyncio.create_task(
#                 session.put(
#                     'http://localhost:8000/products/test1',
#                     json={
#                         'operation': 'add',
#                         'quantity': 1,
#                         'version': 1
#                     }
#                 )
#             ))
#         results = await asyncio.gather(*tasks, return_exceptions=True)

#         # Check that only one update succeeded and others failed with version mismatch
#         successes = len([r for r in results if not isinstance(r, Exception)])
#         assert successes == 1
# ```
# """
