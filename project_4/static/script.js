const API_URL = '/tasks/';
const tasksList = document.getElementById('tasks-list');
const taskForm = document.getElementById('task-form');
const taskCount = document.getElementById('task-count');

// Fetch all tasks on load
document.addEventListener('DOMContentLoaded', fetchTasks);

// Add new task
taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-desc').value;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                description,
                completed: false
            }),
        });

        if (response.ok) {
            document.getElementById('task-title').value = '';
            document.getElementById('task-desc').value = '';
            fetchTasks();
        }
    } catch (error) {
        console.error('Error adding task:', error);
    }
});

async function fetchTasks() {
    try {
        const response = await fetch(API_URL);
        const tasks = await response.json();
        renderTasks(tasks);
        updateCount(tasks.length);
    } catch (error) {
        console.error('Error fetching tasks:', error);
        tasksList.innerHTML = '<p class="error-msg">Failed to load tasks</p>';
    }
}

function renderTasks(tasks) {
    tasksList.innerHTML = '';

    if (tasks.length === 0) {
        tasksList.innerHTML = `
            <div class="empty-state">
                <p>No tasks yet. Add one above!</p>
            </div>
        `;
        return;
    }

    tasks.forEach(task => {
        const taskCard = document.createElement('div');
        taskCard.className = `task-card ${task.completed ? 'completed' : ''}`;

        taskCard.innerHTML = `
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.title)}</div>
                ${task.description ? `<div class="task-desc">${escapeHtml(task.description)}</div>` : ''}
            </div>
            <div class="task-actions">
                <button class="btn-action btn-complete" onclick="toggleTask('${task.id}', ${!task.completed})" title="${task.completed ? 'Mark as incomplete' : 'Mark as complete'}">
                    <i class="fas ${task.completed ? 'fa-undo' : 'fa-check'}"></i>
                </button>
                <button class="btn-action btn-delete" onclick="deleteTask('${task.id}')" title="Delete task">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        tasksList.appendChild(taskCard);
    });
}

async function toggleTask(id, completed) {
    // We need to fetch the current task details first because the PUT endpoint expects the full Task object
    // However, the current implementation of PUT /tasks/{task_id} in main.py expects a Task object
    // and updates the task. Ideally, we should use PATCH for partial updates, but let's work with what we have.

    try {
        // First get the task to preserve title and description
        const getResponse = await fetch(`${API_URL}${id}`);
        if (!getResponse.ok) return;
        const currentTask = await getResponse.json();

        const response = await fetch(`${API_URL}${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...currentTask,
                completed: completed
            }),
        });

        if (response.ok) {
            fetchTasks();
        }
    } catch (error) {
        console.error('Error toggling task:', error);
    }
}

async function deleteTask(id) {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
        const response = await fetch(`${API_URL}${id}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            fetchTasks();
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

function updateCount(count) {
    taskCount.textContent = `${count} task${count !== 1 ? 's' : ''}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
