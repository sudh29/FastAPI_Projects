# Secure Inventory Service

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A robust inventory management service focusing on security, reliability, and concurrency control.

## 🌟 Highlights

- 🛡️ **Basic Authentication** - Secure access to API endpoints.
- 🚦 **Rate Limiting** - Protection against abuse using `slowapi`.
- 🔒 **Concurrency Control** - Async locks to prevent race conditions during updates.
- ⚡ **In-Memory Storage** - High-performance data handling with Python dictionaries.
- 🚨 **Low Stock Alerts** - Caching mechanism for efficient alert retrieval.

---

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Start the application
docker-compose up -d --build

# Stop the application
docker-compose down
```

### Option 2: Running Locally

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```

Visit **http://localhost:8000** to access the application.

**Default Credentials:**
- Username: `admin`
- Password: `admin`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products` | List all products |
| `GET` | `/products/{id}` | Get product details |
| `POST` | `/products` | Create new product |
| `PUT` | `/products/{id}` | Update product details |
| `PATCH` | `/products/{id}/inventory` | Update stock quantity |
| `DELETE` | `/products/{id}` | Delete product |
| `GET` | `/products/alerts` | Get low stock alerts |

---

## 💻 Tech Stack

- **Backend**: FastAPI
- **Security**: HTTP Basic Auth
- **Rate Limiting**: SlowAPI
- **Concurrency**: Asyncio Locks

## 📂 Project Structure

```
project_7/
├── main.py              # Main application logic
├── static/              # Static assets
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```
