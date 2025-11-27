You are asked to build a real-time product inventory service using FastAPI. Your solution will be evaluated on correctness, robustness (error handling), concurrency safety, and performance optimization.

📋 Requirements
Core Functionality

Add Products:
POST /products — create a new product with fields:

json
Copy
Edit
{ "id": str, "name": str, "price": float, "quantity": int }
Get Product:
GET /products/{id} — retrieve a product’s details.

Update Inventory:
PATCH /products/{id}/inventory — adjust stock by delta: int (positive or negative).

List Low-Stock Alerts:
GET /products/alerts?threshold={n} — list all products whose quantity ≤ threshold.

Real-Time Concurrency

Implement safe concurrent updates (e.g., two clients reducing the same item at once).

Demonstrate your approach (e.g., optimistic locking, Redis mutex, database transactions).

Error Handling

Return meaningful HTTP status codes (4xx/5xx) and JSON error bodies.

Gracefully handle scenarios like “product not found” or “insufficient stock.”

Performance Optimization

Use asynchronous I/O end-to-end (async endpoints, async DB drivers).

Add caching for read-heavy endpoints (e.g., using in-memory cache or Redis).

Include at least one benchmark or load-test demonstrating throughput/latency improvements.

Testing

Provide unit or integration tests (e.g., pytest + HTTPX).

Cover happy paths, failure modes, and concurrent update scenarios.

📂 Deliverables
A Git repo (or zip) containing:

app/ — FastAPI application code

tests/ — test suite

requirements.txt (or poetry.toml / Pipfile)

README.md with:

Setup & run instructions

Description of your concurrency strategy

Summary of performance benchmarks (e.g., wrk or locust results)

🏆 Evaluation Criteria
Area Focus
Correctness Endpoints work as specified
Error Handling Clear, consistent HTTP errors & messages
Concurrency Safety No lost updates or race conditions
Performance Async I/O, caching, benchmark results
Code Quality & Tests Readable, well-structured, covered by tests
