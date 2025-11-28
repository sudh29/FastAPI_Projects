# FastAPI Todo App

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, full-stack Todo application built with **FastAPI** and **Vanilla JavaScript**, featuring a persistent SQLite database and a premium glassmorphism UI.

## 🌟 Highlights

- 🗄️ **Persistent Storage** - SQLite database integration using SQLAlchemy ORM.
- 🎨 **Modern GUI** - Beautiful, responsive interface with glassmorphism design and animations.
- ⚡ **Full CRUD** - Create, Read, Update, and Delete tasks seamlessly.
- 🏷️ **Priority System** - Organize tasks with priority levels (Low to Critical).
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

Visit **http://localhost:8000** to use the application.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/todos` | Fetch all todo items |
| `GET` | `/todo/{id}` | Fetch a specific todo item |
| `POST` | `/todo` | Create a new todo item |
| `PUT` | `/todo/{id}` | Update an existing todo item |
| `DELETE` | `/todo/{id}` | Delete a todo item |

---

## 💻 Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JavaScript
- **Database**: SQLite
- **Python**: 3.12+

## 📂 Project Structure

```
project_3/
├── main.py              # FastAPI application
├── models.py            # SQLAlchemy models
├── database.py          # Database configuration
├── templates/           # HTML templates
├── static/              # CSS and JS assets
├── Dockerfile          # Docker build instructions
├── docker-compose.yml  # Docker services configuration
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```
