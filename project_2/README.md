# FastAPI Books API (Pydantic)

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enhanced RESTful API for managing a book collection, leveraging **Pydantic** models for robust data validation and **FastAPI** for high performance.

## 🌟 Highlights

- 🛡️ **Data Validation** - Strong typing and validation using Pydantic models.
- 🆔 **ID-Based Management** - Manage books reliably using unique IDs.
- 🔍 **Advanced Filtering** - Filter books by rating and publication date.
- 📄 **Interactive Docs** - Automatic Swagger UI documentation.
- 🐳 **Docker Ready** - Easy deployment with Docker Compose.

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

Visit **http://localhost:8000** to see the application running.

---

## 🔌 API Endpoints

The API provides the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/books` | Get all books (optional filters: `rating`, `published_date`) |
| `GET` | `/books/{book_id}` | Get a specific book by ID |
| `POST` | `/create-book` | Add a new book to the collection |
| `PUT` | `/books/update_book` | Update an existing book |
| `DELETE` | `/books/{book_id}` | Delete a book by ID |

You can explore and test the API at **http://localhost:8000/docs**.

---

## 💻 Tech Stack

- **Framework**: FastAPI
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Language**: Python 3.12+

## 📂 Project Structure

```
project_2/
├── main.py              # FastAPI application with Pydantic models
├── static/              # Frontend assets (if applicable)
├── templates/           # Jinja2 templates (if applicable)
├── Dockerfile          # Docker build instructions
├── docker-compose.yml  # Docker services configuration
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```
