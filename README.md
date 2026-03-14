# FastAPI Projects Collection

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive collection of FastAPI applications demonstrating various features, patterns, and best practices in modern web development.
New changes

## 📂 Projects Overview

| Project                  | Name                     | Description                         | Key Features                          |
| ------------------------ | ------------------------ | ----------------------------------- | ------------------------------------- |
| [Project 1](./project_1) | **Books API (Basic)**    | Simple REST API for managing books. | Basic CRUD, Docker support.           |
| [Project 2](./project_2) | **Books API (Pydantic)** | Enhanced Books API with validation. | Pydantic models, ID-based routing.    |
| [Project 3](./project_3) | **Todo App**             | Full-stack Todo application.        | SQLite, Glassmorphism UI.             |
| [Project 4](./project_4) | **Task Manager**         | Task management API.                | Task CRUD, Modern UI.                 |
| [Project 5](./project_5) | **Advanced Todo App**    | Secure Todo app with roles.         | Authentication, Admin roles, Routers. |
| [Project 6](./project_6) | **Full-Stack Todo**      | Complete Todo solution.             | JWT Auth, Bootstrap + Custom CSS.     |
| [Project 7](./project_7) | **Secure Inventory**     | Secure inventory service.           | Rate Limiting, Basic Auth, Locks.     |
| [Project 8](./project_8) | **Enterprise Inventory** | High-scale inventory system.        | Circuit Breakers, SSE, Bulk Ops.      |
| [Project 9](./project_9) | **Crypto Portfolio**     | Full-stack Crypto Tracker.          | React Frontend, Binance API, JWT.     |

---

## 🚀 General Setup Instructions

These instructions apply to most projects. Check individual `README.md` files for specific details.

### 1. Install `uv` (Recommended)

We use `uv` for fast Python package management.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Run a Project

Navigate to the project directory and run:

```bash
cd project_X
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Using Docker

Most projects support Docker Compose:

```bash
cd project_X
docker-compose up -d --build
```

---

## 📝 License

This repository is licensed under the MIT License.
