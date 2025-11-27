# TodoApp - FastAPI Project

This project is a FastAPI-based Todo application with authentication, user management, and CRUD operations for todos. It includes a web interface and a full test suite.

## Features

- User registration and authentication
- Admin and user roles
- CRUD operations for todos
- HTML templates for web pages
- Static files for CSS/JS
- Pytest-based test suite

## Getting Started

### Install dependencies

```bash
uv pip install -r requirements.txt
```

### Run the application

```bash
uv run python -m TodoApp.main
```

Or with Uvicorn directly:

```bash
uvicorn TodoApp.main:app --reload
```

### Run tests

```bash
uv run pytest
```

Or for a specific test file:

```bash
uv run pytest test.py
```

## Project Structure

```
TodoApp/
├── main.py
├── routers/
│   ├── auth.py
│   ├── todos.py
│   ├── admin.py
│   └── users.py
├── models.py
├── database.py
├── templates/
│   └── ...
├── static/
│   └── ...
├── test/
│   └── ...
├── README.md
├── requirements.txt
```

## API Endpoints

- `/auth/` - Authentication routes
- `/todos/` - Todo CRUD routes
- `/admin/` - Admin-only routes
- `/user/` - User profile routes
- `/healthy` - Health check
