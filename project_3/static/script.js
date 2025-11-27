function init() {
    const todoList = document.getElementById('todo-list');
    const addTodoForm = document.getElementById('add-todo-form');
    const editModal = document.getElementById('edit-modal');
    const editForm = document.getElementById('edit-todo-form');
    const closeModal = document.querySelector('.close-modal');
    const cancelEdit = document.getElementById('cancel-edit');

    // State
    let allTodos = [];
    let currentFilter = 'all';

    // Fetch and render todos
    fetchTodos();

    // Filter Listeners
    document.querySelectorAll('input[name="filter"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentFilter = e.target.value;
            applyFilterAndRender();
        });
    });

    // Event Delegation for Todo List Actions
    if (todoList) {
        todoList.addEventListener('click', (e) => {
            const target = e.target;

            // Handle Delete
            const deleteBtn = target.closest('.delete');
            if (deleteBtn) {
                const id = parseInt(deleteBtn.dataset.id);
                if (isNaN(id)) return;
                deleteTodo(id);
                return;
            }

            // Handle Edit
            const editBtn = target.closest('.edit-btn');
            if (editBtn) {
                const id = parseInt(editBtn.dataset.id);
                openEditModal(id);
                return;
            }
        });

        todoList.addEventListener('change', (e) => {
            if (e.target.classList.contains('todo-checkbox')) {
                const id = parseInt(e.target.dataset.id);
                toggleComplete(id, e.target.checked);
            }
        });
    }

    async function fetchTodos() {
        try {
            const response = await fetch('/todos');
            if (!response.ok) throw new Error('Failed to fetch todos');
            allTodos = await response.json();
            applyFilterAndRender();
        } catch (error) {
            console.error('Error fetching todos:', error);
            if (todoList) {
                todoList.innerHTML = '<p class="error">Failed to load tasks. Please try again.</p>';
            }
        }
    }

    function applyFilterAndRender() {
        let filteredTodos = allTodos;

        if (currentFilter !== 'all') {
            const priority = parseInt(currentFilter);
            filteredTodos = allTodos.filter(todo => todo.priority === priority);
        }

        renderTodos(filteredTodos);
    }

    function renderTodos(todos) {
        if (!todoList) return;
        todoList.innerHTML = '';

        if (todos.length === 0) {
            const message = currentFilter === 'all'
                ? 'No tasks yet. Add one above!'
                : `No tasks with ${getPriorityLabel(parseInt(currentFilter))} priority.`;

            todoList.innerHTML = `
                <div class="empty-state" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                    <i class="fas fa-clipboard-list" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>${message}</p>
                </div>
            `;
            return;
        }

        // Sort todos: Incomplete first, then by priority (desc)
        todos.sort((a, b) => {
            if (a.complete === b.complete) {
                return b.priority - a.priority;
            }
            return a.complete ? 1 : -1;
        });

        todos.forEach(todo => {
            const item = document.createElement('div');
            item.className = `todo-item ${todo.complete ? 'completed' : ''}`;
            item.innerHTML = `
                <div class="todo-content">
                    <input type="checkbox" class="todo-checkbox"
                        ${todo.complete ? 'checked' : ''}
                        data-id="${todo.id}">
                    <div class="todo-text">
                        <span class="todo-title">${escapeHtml(todo.title)}</span>
                        <span class="todo-desc">${escapeHtml(todo.description || '')}</span>
                    </div>
                </div>
                <div class="todo-meta">
                    <span class="priority-badge priority-${todo.priority}">${getPriorityLabel(todo.priority)}</span>
                    <div class="actions">
                        <button class="icon-btn edit-btn" data-id="${todo.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="icon-btn delete" data-id="${todo.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            todoList.appendChild(item);
        });
    }

    // Add Todo
    if (addTodoForm) {
        addTodoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            const priority = document.querySelector('input[name="priority"]:checked').value;

            const newTodo = {
                title,
                description,
                priority: parseInt(priority),
                complete: false
            };

            try {
                const response = await fetch('/todo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newTodo)
                });

                if (response.ok) {
                    addTodoForm.reset();
                    // Reset priority to 3 (High)
                    const p3 = document.getElementById('p3');
                    if (p3) p3.checked = true;
                    fetchTodos();
                } else {
                    alert('Failed to add task');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Toggle Complete
    async function toggleComplete(id, isComplete) {
        const todo = allTodos.find(t => t.id === id);
        if (!todo) return;

        const updatedTodo = {
            ...todo,
            complete: isComplete
        };

        const payload = {
            title: updatedTodo.title,
            description: updatedTodo.description,
            priority: updatedTodo.priority,
            complete: updatedTodo.complete
        };

        try {
            await fetch(`/todo/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            fetchTodos();
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Delete Todo
    async function deleteTodo(id) {
        if (!confirm('Are you sure you want to delete this task?')) return;

        try {
            const response = await fetch(`/todo/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                fetchTodos();
            } else {
                console.error('Failed to delete task:', response.status);
                alert('Failed to delete task. Please try again.');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            alert('An error occurred while deleting the task.');
        }
    }

    // Edit Modal Logic
    function openEditModal(id) {
        const todo = allTodos.find(t => t.id === id);
        if (!todo) return;

        document.getElementById('edit-id').value = id;
        document.getElementById('edit-title').value = todo.title;
        document.getElementById('edit-description').value = todo.description || '';

        const priorityRadio = document.querySelector(`input[name="edit-priority"][value="${todo.priority}"]`);
        if (priorityRadio) priorityRadio.checked = true;

        // Store complete status for saving
        editForm.dataset.complete = todo.complete;

        if (editModal) editModal.style.display = 'flex';
    }

    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('edit-id').value;
            const title = document.getElementById('edit-title').value;
            const description = document.getElementById('edit-description').value;
            const priority = document.querySelector('input[name="edit-priority"]:checked').value;
            const complete = editForm.dataset.complete === 'true';

            const updatedTodo = {
                title,
                description,
                priority: parseInt(priority),
                complete
            };

            try {
                const response = await fetch(`/todo/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updatedTodo)
                });

                if (response.ok) {
                    closeEditModal();
                    fetchTodos();
                } else {
                    alert('Failed to update task');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    function closeEditModal() {
        if (editModal) editModal.style.display = 'none';
    }

    if (closeModal) closeModal.onclick = closeEditModal;
    if (cancelEdit) cancelEdit.onclick = closeEditModal;
    window.onclick = (e) => {
        if (e.target === editModal) closeEditModal();
    };

    // Helpers
    function getPriorityLabel(p) {
        const labels = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent', 5: 'Critical' };
        return labels[p] || 'Unknown';
    }

    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
