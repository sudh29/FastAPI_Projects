# FastAPI Task Manager

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A high-performance RESTful API built with FastAPI for managing tasks, featuring a modern, responsive web interface with glassmorphism design.

## 🌟 Highlights

- 🚀 **High Performance** - Built on Starlette and Pydantic
- 🎨 **Modern GUI** - Beautiful, responsive interface with glassmorphism design
- 🐳 **Docker Ready** - Production-optimized Docker setup
- 📄 **Interactive Docs** - Automatic Swagger UI documentation
- ✨ **Real-time Updates** - Dynamic task management

---

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

**Using Docker Compose:**
```bash
# Start the application
docker-compose up -d --build

# Stop the application
docker-compose down
```

**Using Dockerfile:**
```bash
# Build the image
docker build -t fastapi-tasks-api .

# Run the container
docker run -d -p 8000:8000 --name fastapi-tasks-api fastapi-tasks-api

# View logs
docker logs -f fastapi-tasks-api

# Stop and remove
docker stop fastapi-tasks-api
docker rm fastapi-tasks-api
```

### Option 2: Running Locally (using uv)

```bash
# Create virtual environment
uv venv

# Activate virtual environment
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
| `GET` | `/tasks/` | Get all tasks |
| `GET` | `/tasks/{task_id}` | Get task by ID |
| `POST` | `/tasks/` | Create a new task |
| `PUT` | `/tasks/{task_id}` | Update an existing task |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

You can also explore the interactive API documentation at **http://localhost:8000/docs**.

---

## 💻 Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JavaScript
- **Containerization**: Docker, Docker Compose
- **Python**: 3.12+

## 📂 Project Structure

```
project_4/
├── main.py              # FastAPI application
├── static/              # Frontend assets
│   ├── index.html      # Main GUI
│   ├── style.css       # Styles
│   └── script.js       # Frontend logic
├── Dockerfile          # Docker build instructions
├── docker-compose.yml  # Docker services configuration
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

## 📝 License

This project is licensed under the MIT License.
