# FastAPI Books API (Basic)

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


A lightweight, foundational RESTful API for managing a book collection. This project demonstrates the core concepts of FastAPI without external database dependencies, using in-memory Python dictionaries.

## 🌟 Highlights

- ⚡ **Lightweight** - No database required, runs entirely in memory.
- 🚀 **FastAPI Basics** - Demonstrates path parameters, query parameters, and body requests.
- 📂 **Dictionary Storage** - Simple data manipulation using Python lists and dictionaries.
- 🐳 **Docker Ready** - Production-optimized Docker setup.
- 📄 **Interactive Docs** - Automatic Swagger UI documentation.

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

Visit **http://localhost:8000** to use the application.

---

## 🔌 API Endpoints

The API provides the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/books` | Get all books |
| `GET` | `/books/{book_title}` | Get book by title |
| `GET` | `/books/` | Filter books by category |
| `GET` | `/books/byauthor/` | Filter books by author |
| `POST` | `/books/create_book` | Add a new book |
| `PUT` | `/books/update_book` | Update an existing book |
| `DELETE` | `/books/delete_book/{book_title}` | Delete a book |

You can also explore the interactive API documentation at **http://localhost:8000/docs**.

---

## 💻 Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Storage**: In-memory (Python Dicts)
- **Containerization**: Docker, Docker Compose
- **Python**: 3.12+

## 📂 Project Structure

```
project_1/
├── main.py              # FastAPI application (Dictionary based)
├── static/              # Frontend assets
├── Dockerfile          # Docker build instructions
├── docker-compose.yml  # Docker services configuration
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```
