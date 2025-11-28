# Crypto Portfolio Tracker (Project 9)

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-stack cryptocurrency portfolio tracking application built with **FastAPI** (Backend) and **React + Vite** (Frontend).

## 🚀 Features

*   **User Authentication**: Secure registration and login with JWT and password hashing (Bcrypt).
*   **Portfolio Management**: Track your total portfolio value, available cash, and invested assets.
*   **Real-time Prices**: Fetches live cryptocurrency prices from Binance API.
*   **Trading Simulation**: Buy and sell assets with real-time market data.
*   **Performance Tracking**: View absolute and relative performance of your investments.
*   **Responsive Design**: Modern, glassmorphism-inspired UI built with Tailwind CSS.

## 🛠️ Tech Stack

### Backend
*   **Framework**: FastAPI
*   **Database**: SQLite (SQLAlchemy ORM)
*   **Authentication**: PyJWT, Passlib (Bcrypt)
*   **API Client**: Requests (for Binance API)

### Frontend
*   **Framework**: React (Vite)
*   **Styling**: Tailwind CSS v4
*   **State Management**: React Context API
*   **Routing**: React Router DOM
*   **HTTP Client**: Axios

## 📋 Prerequisites

*   **Docker** and **Docker Compose** (Recommended)
*   *Or* **Python 3.12+** and **Node.js 20+** (for local execution)

## 🏃‍♂️ How to Run

### Option 1: Using Docker (Recommended)

This is the easiest way to run the entire application.

1.  **Build and Start the containers**:
    ```bash
    docker-compose up --build

    docker-compose down
    ```

2.  **Access the Application**:
    *   **Frontend**: [http://localhost:5173](http://localhost:5173)
    *   **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)


    ```bash
    # Remove the existing containers manually
    docker rm -f crypto_backend crypto_frontend

    # Remove the build cache and orphans to be safe
    docker-compose down --volumes --remove-orphans

    # Now rebuild and start fresh
    docker-compose up --build
    ```

### Option 2: Using Python Script (Local)

We have provided a convenience script to run both services concurrently.

1.  **Install Backend Dependencies**:
    ```bash
    cd backend
    pip install -r requirements.txt
    cd ..
    ```

2.  **Install Frontend Dependencies**:
    ```bash
    cd frontend
    npm install
    cd ..
    ```

3.  **Run the Project**:
    ```bash
    python run.py
    ```

### Option 3: Manual Setup (Local)

**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## 🧪 API Endpoints

*   `POST /register`: Create a new account.
*   `POST /login`: Authenticate and get a JWT token.
*   `GET /portfolio`: Get portfolio summary and assets.
*   `POST /add-money`: Add funds to your account.
*   `POST /buy`: Buy a cryptocurrency.
*   `POST /sell`: Sell a cryptocurrency.

## 📝 Notes

*   The application uses a local SQLite database (`crypto_portfolio.db`).
*   Live prices are fetched from the public Binance API.
*   **Default Port**: Backend runs on `8000`, Frontend on `5173`.
