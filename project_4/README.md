# FastAPI Task Manager

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A streamlined Task Manager API built with **FastAPI**, utilizing **UUIDs** for unique task identification and **Pydantic** for data validation.

## 🌟 Highlights

- 🆔 **UUID Support** - Uses standard UUIDs for robust unique identification of tasks.
- 📝 **Pydantic Models** - Strong typing and validation for task creation and updates.
- ⚡ **In-Memory Speed** - Fast operations using in-memory list storage.
- 🎨 **Modern GUI** - Includes a responsive web interface.
- 🐳 **Docker Ready** - Production-optimized Docker setup.

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

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tasks/` | Get all tasks |
| `GET` | `/tasks/{task_id}` | Get task by UUID |
| `POST` | `/tasks/` | Create a new task |
| `PUT` | `/tasks/{task_id}` | Update an existing task |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

---

## 💻 Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Validation**: Pydantic
- **Frontend**: HTML5, CSS3, JavaScript
- **Python**: 3.12+

## 📂 Project Structure

```
project_4/
├── main.py              # FastAPI application with UUIDs
├── static/              # Frontend assets
├── Dockerfile          # Docker build instructions
├── docker-compose.yml  # Docker services configuration
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```
