# Enterprise Inventory System

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A high-performance, enterprise-grade inventory management system designed for scalability and reliability.

## 🌟 Highlights

- ⚡ **High Performance** - Optimized for speed with async operations.
- 🛡️ **Circuit Breakers** - Fault tolerance for external dependencies or high load.
- 🌊 **Real-time Streaming** - Server-Sent Events (SSE) for live inventory updates.
- 📦 **Bulk Operations** - Efficient bulk update endpoints.
- 🔄 **Background Tasks** - Asynchronous processing for webhooks and heavy tasks.
- 🚦 **Rate Limiting** - Advanced rate limiting per client.

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

Visit **http://localhost:8000** to access the dashboard.

---

## 🔌 API Endpoints

### Core Inventory
- `GET /products` - List products
- `POST /products` - Create product
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Advanced Features
- `POST /products/bulk` - Bulk update inventory
- `GET /products/{id}/stream` - Subscribe to real-time updates (SSE)
- `POST /webhook/supplier` - Handle supplier updates via webhook

---

## 💻 Tech Stack

- **Backend**: FastAPI
- **Architecture**: AsyncIO, Event-driven
- **Resilience**: Circuit Breaker Pattern
- **Real-time**: Server-Sent Events (SSE)

## 📂 Project Structure

```
project_8/
├── main.py              # Complex application logic
├── static/              # Frontend assets
├── templates/           # Dashboard templates
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```
