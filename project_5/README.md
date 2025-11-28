# FastAPI Advanced Todo App

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-featured Todo application built with **FastAPI**, featuring robust user authentication, role-based access control, and a server-side rendered UI.

## 🌟 Highlights

- 🔐 **Authentication** - Secure user registration and login (JWT).
- 👮 **Role-Based Access** - Admin and User roles with specific permissions.
- 🗄️ **Database Integration** - SQLite database with SQLAlchemy ORM.
- 🌐 **Web Interface** - Server-side rendered HTML using Jinja2 templates.
- 🧩 **Modular Design** - Organized code using FastAPI Routers.

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
- `POST /auth/` - Register new user
- `POST /auth/token` - Login

### Todos
- `GET /todos` - List all todos
- `POST /todos/todo` - Create todo
- `PUT /todos/todo/{id}` - Update todo
- `DELETE /todos/todo/{id}` - Delete todo

### Admin
- `GET /admin/todo` - View all todos (Admin only)
- `DELETE /admin/todo/{id}` - Delete any todo (Admin only)

### Users
- `GET /user` - Get current user profile
- `PUT /user/password` - Change password

---

## 💻 Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Database**: SQLite, SQLAlchemy
- **Templating**: Jinja2
- **Security**: PyJWT, Passlib (Bcrypt)

## 📂 Project Structure

```
project_5/
├── main.py              # Application entry point
├── models.py            # Database models
├── database.py          # Database configuration
├── routers/             # API routes (auth, todos, admin, users)
├── templates/           # HTML templates
├── static/              # CSS and JS assets
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```
