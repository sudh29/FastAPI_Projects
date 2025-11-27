# Todo App (Project 3)

A modern, full-stack Todo application built with FastAPI and vanilla JavaScript.

## Features

-   **FastAPI Backend**: Robust API with SQLite database integration using SQLAlchemy.
-   **Modern GUI**: Premium glassmorphism design with animated background blobs.
-   **Task Management**: Create, read, update, and delete tasks.
-   **Priority System**: Assign priorities (Low, Medium, High, Urgent, Critical) to tasks.
-   **Filtering**: Filter tasks by priority level.
-   **Responsive Design**: Works seamlessly on desktop and mobile devices.

## Project Structure

-   `main.py`: The FastAPI application entry point.
-   `models.py`: SQLAlchemy database models.
-   `database.py`: Database configuration.
-   `templates/index.html`: The main HTML interface.
-   `static/style.css`: CSS styles for the glassmorphism UI.
-   `static/script.js`: Client-side logic for API interaction and DOM manipulation.

## Setup and Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    uvicorn main:app --reload
    ```
    Or simply:
    ```bash
    python main.py
    ```

3.  **Access the App**:
    Open your browser and navigate to `http://127.0.0.1:8000`.

## API Endpoints

-   `GET /`: Serves the main UI.
-   `GET /todos`: Fetch all todo items.
-   `GET /todo/{id}`: Fetch a specific todo item.
-   `POST /todo`: Create a new todo item.
-   `PUT /todo/{id}`: Update an existing todo item.
-   `DELETE /todo/{id}`: Delete a todo item.

## Technologies Used

-   **Backend**: Python, FastAPI, SQLAlchemy, SQLite
-   **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
-   **Design**: Glassmorphism, CSS Animations, Google Fonts (Outfit)


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
docker build -t fastapi-todo-app .

# Run the container
docker run -d -p 8000:8000 --name fastapi-todo-app fastapi-todo-app

# View logs
docker logs -f fastapi-todo-app

# Stop and remove
docker stop fastapi-todo-app
docker rm fastapi-todo-app
```
