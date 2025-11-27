# Chapter 4 - FastAPI Todo App

This project demonstrates building a Todo application using FastAPI, including authentication, user management, and CRUD operations for todos. It also includes a test suite using pytest.

## Features

- User registration and authentication
- CRUD operations for todos
- Admin and user roles
- Health check endpoint
- Pytest-based tests

## Getting Started

### Install dependencies

```bash
uv pip install -r requirements.txt
```

### Run the application

```bash
uv run python -m main
```

Or with Uvicorn directly:

```bash
uvicorn main:app --reload
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
chapter_4/
├── main.py
├── routers/
│   ├── auth.py
│   ├── todos.py
│   ├── admin.py
│   └── users.py
├── models.py
├── database.py
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
