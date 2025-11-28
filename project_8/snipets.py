# 1. Async SQLAlchemy Dependency (FastAPI)
# ✅ Fix:
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import redis
import json
import os
import asyncio
from typing import List, Optional

# Note: In a real app, use environment variables for the database URL
engine = create_async_engine("sqlite+aiosqlite:///./test.db")
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


# Example usage:
# @app.get("/items/")
# async def read_items(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Item))
#     return result.scalars().all()


# 2. AWS Lambda Redis Handler

# Use environment variable for host
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST)


def lambda_handler(event, context):
    try:
        # Assuming 'key' is passed in event or fixed
        key = event.get("key", "default_key")
        result = redis_client.get(key)
        return {
            "statusCode": 200,
            "body": json.dumps(result.decode() if result else "Not Found"),
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}


# 3. Sequential Async Processing


async def long_computation(item):
    # Simulate work
    await asyncio.sleep(1)
    return item * 2


async def process_items(items):
    # Use asyncio.gather for concurrency
    return await asyncio.gather(*(long_computation(item) for item in items))


# 4. eval() Usage in FastAPI Endpoint

# pip install simpleeval
# from simpleeval import simple_eval

# @app.post("/process")
# async def process(data: Dict[str, Any]):
#     try:
#         # result = simple_eval(data['expression'])
#         # For now, just returning a safe message as simpleeval might not be installed
#         return {"result": "Safe evaluation not implemented in this snippet"}
#     except Exception as e:
#         return {"error": str(e)}


# 5. Global Counter with Race Condition
counter = 0
lock = asyncio.Lock()


async def increment():
    global counter
    async with lock:
        counter += 1


# 6. Invalid Type Annotations


# For Python < 3.10:
def process_legacy(data: Optional[List[str]]) -> str:
    return "processed"


# For Python >= 3.10:
def process_modern(data: list[str] | None) -> str:
    return "processed"
