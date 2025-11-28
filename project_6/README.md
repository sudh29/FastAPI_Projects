# Full-Stack Todo Application

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, full-stack Todo application featuring **User Authentication**, **Database Integration**, and a polished **Bootstrap** frontend served via Jinja2 templates.

## 🌟 Highlights

- 🔐 **Secure Authentication** - Full user registration and login flow using JWT.
- 🗄️ **Database Driven** - SQLite database with SQLAlchemy ORM for reliable data persistence.
- 🎨 **Bootstrap UI** - Clean, responsive interface built with Bootstrap and custom CSS.
- 🧩 **Modular Architecture** - Organized codebase using FastAPI Routers for scalability.
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

Visit **http://localhost:8000** to access the application.

---

## 🔌 API Endpoints

### Authentication
- `GET /auth/login-page` - Login Page
- `GET /auth/register-page` - Registration Page
- `POST /auth/token` - Authenticate User

### Todos
- `GET /todos/todo-page` - Main Dashboard
- `GET /todos/` - List Todos
- `POST /todos/todo` - Create Todo
- `PUT /todos/todo/{id}` - Update Todo
- `DELETE /todos/todo/{id}` - Delete Todo

---

## 💻 Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy
- **Frontend**: HTML5, Bootstrap, Jinja2 Templates
- **Security**: PyJWT, Passlib (Bcrypt)
- **Database**: SQLite

## 📂 Project Structure

```
project_6/
├── main.py              # Application entry point
├── models.py            # Database models
├── database.py          # Database configuration
├── routers/             # API routes (auth, todos, admin, users)
├── templates/           # HTML templates
├── static/              # CSS and JS assets
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```
