from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4

app = FastAPI()


class Task(BaseModel):
    """
    Represents a task in the CRUD application.

    Attributes:
        id (Optional[UUID]): Unique identifier for the task.
        title (str): Title of the task.
        description (Optional[str]): Description of the task.
        completed (bool): Status of the task (completed or not).
    """

    id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    completed: bool = False


tasks: List[Task] = []


@app.post("/tasks/", response_model=Task)
def create_task(task: Task) -> Task:
    """
    Create a new task and add it to the list.

    Args:
        task (Task): The task to create.
    Returns:
        Task: The created task with a generated UUID.
    """
    task.id = uuid4()
    tasks.append(task)
    return task


@app.get("/tasks/", response_model=List[Task])
def read_tasks() -> List[Task]:
    """
    Retrieve all tasks.

    Returns:
        List[Task]: List of all tasks.
    """
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: UUID) -> Task:
    """
    Retrieve a specific task by its ID.

    Args:
        task_id (UUID): The ID of the task to retrieve.
    Returns:
        Task: The task with the specified ID.
    Raises:
        HTTPException: If the task is not found.
    """
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: UUID, task_update: Task) -> Task:
    """
    Update an existing task by its ID.

    Args:
        task_id (UUID): The ID of the task to update.
        task_update (Task): The updated task data.
    Returns:
        Task: The updated task.
    Raises:
        HTTPException: If the task is not found.
    """
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = task.copy(update=task_update.dict(exclude_unset=True))
            tasks[idx] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: UUID) -> Task:
    """
    Delete a task by its ID.

    Args:
        task_id (UUID): The ID of the task to delete.
    Returns:
        Task: The deleted task.
    Raises:
        HTTPException: If the task is not found.
    """
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            return tasks.pop(idx)
    raise HTTPException(status_code=404, detail="Task not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
