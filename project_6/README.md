# FastAPI Todo App

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-featured Todo application built with FastAPI, featuring user authentication, database integration, and a modern responsive web interface.

## 🌟 Highlights

- 🚀 **Full-Stack Application** - FastAPI backend with Jinja2 templates for the frontend.
- 🔐 **Authentication** - Secure user registration and login with JWT tokens.
- 📝 **Todo Management** - Create, read, update, and delete (CRUD) todo items.
- 🎨 **Modern GUI** - Clean and responsive interface using Bootstrap and custom CSS.
- 🗄️ **Database** - SQLite database with SQLAlchemy ORM.

---

## 🚀 Quick Start

### Running Locally

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the virtual environment:**
    - Windows: `venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    uvicorn main:app --reload
    ```

5.  **Access the application:**
    Open your browser and go to [http://localhost:8000](http://localhost:8000).

---

## 🔌 API Endpoints

The API provides the following main endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Redirects to the main todo page |
| `GET` | `/auth/login-page` | Login page |
| `GET` | `/auth/register-page` | Registration page |
| `GET` | `/todos/todo-page` | Main dashboard (requires login) |
| `POST` | `/auth/` | Register a new user |
| `POST` | `/auth/token` | Login and get access token |
| `GET` | `/todos/` | Get all todos for the user |
| `POST` | `/todos/todo` | Create a new todo |
| `PUT` | `/todos/todo/{id}` | Update a todo |
| `DELETE` | `/todos/todo/{id}` | Delete a todo |

You can also explore the interactive API documentation at **http://localhost:8000/docs**.

---

## 💻 Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy
- **Frontend**: HTML5, CSS3 (Bootstrap + Custom), Jinja2 Templates, Vanilla JavaScript
- **Database**: SQLite
- **Authentication**: JWT (JSON Web Tokens), Passlib (Bcrypt)

## 📂 Project Structure

```
project_6/
├── main.py              # Application entry point
├── models.py            # Database models
├── database.py          # Database configuration
├── routers/             # API routes (auth, todos, admin, users)
├── templates/           # HTML templates
├── static/              # CSS and JS assets
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```


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
docker build -t fastapi-todo .

# Run the container
docker run -d -p 8000:8000 --name fastapi-todo fastapi-todo

# View logs
docker logs -f fastapi-todo

# Stop and remove
docker stop fastapi-todo
docker rm fastapi-todo
```
