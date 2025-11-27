const API_URL = '/books';
let allBooks = [];
let isEditing = false;
let currentBookTitle = '';

// Initial load
document.addEventListener('DOMContentLoaded', fetchAllBooks);

async function fetchAllBooks() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Failed to fetch books');
        allBooks = await response.json();
        renderBooks(allBooks);
        showToast('Books loaded successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error loading books', 'error');
    }
}

function renderBooks(books) {
    const grid = document.getElementById('bookGrid');
    grid.innerHTML = '';

    if (books.length === 0) {
        grid.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: var(--text-secondary);">No books found.</p>';
        return;
    }

    books.forEach(book => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${escapeHtml(book.title)}</h3>
            <p><i class="fas fa-user"></i> ${escapeHtml(book.author)}</p>
            <p><i class="fas fa-tag"></i> ${escapeHtml(book.category)}</p>
            <div class="actions">
                <button onclick="openModal('edit', '${escapeHtml(book.title)}')">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="danger" onclick="deleteBook('${escapeHtml(book.title)}')">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function filterBooks() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const category = document.getElementById('categoryFilter').value.toLowerCase();

    const filtered = allBooks.filter(book => {
        const matchesSearch = book.title.toLowerCase().includes(searchTerm) ||
                            book.author.toLowerCase().includes(searchTerm);
        const matchesCategory = category === '' || book.category.toLowerCase() === category;
        return matchesSearch && matchesCategory;
    });

    renderBooks(filtered);
}

function openModal(mode, title = '') {
    const modal = document.getElementById('bookModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('bookForm');

    isEditing = mode === 'edit';
    currentBookTitle = title;

    modalTitle.textContent = isEditing ? 'Edit Book' : 'Add New Book';
    document.getElementById('submitBtn').textContent = isEditing ? 'Update Book' : 'Add Book';

    if (isEditing) {
        const book = allBooks.find(b => b.title === title);
        if (book) {
            document.getElementById('title').value = book.title;
            document.getElementById('author').value = book.author;
            document.getElementById('category').value = book.category;
            // Disable title editing as it's the key for update/delete in this simple API
            // Actually the API allows updating title if we send the old one?
            // The API uses title to find the book to update:
            // if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            // So we can't easily change the title with the current API logic if we use the new title to search.
            // But wait, the API iterates and checks:
            // if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            // This means the API expects the `updated_book` to have the SAME title as the one being updated.
            // So we effectively cannot change the title with the current API implementation.
            document.getElementById('title').readOnly = true;
            document.getElementById('title').style.opacity = '0.7';
            document.getElementById('title').title = "Title cannot be changed";
        }
    } else {
        form.reset();
        document.getElementById('title').readOnly = false;
        document.getElementById('title').style.opacity = '1';
        document.getElementById('title').title = "";
    }

    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('bookModal').classList.remove('active');
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const bookData = {
        title: document.getElementById('title').value,
        author: document.getElementById('author').value,
        category: document.getElementById('category').value
    };

    try {
        let url, method;

        if (isEditing) {
            url = '/books/update_book';
            method = 'PUT';
        } else {
            url = '/books/create_book';
            method = 'POST';
        }

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookData)
        });

        if (!response.ok) throw new Error('Operation failed');

        closeModal();
        await fetchAllBooks();
        showToast(isEditing ? 'Book updated successfully' : 'Book added successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error saving book', 'error');
    }
}

async function deleteBook(title) {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) return;

    try {
        const response = await fetch(`/books/delete_book/${encodeURIComponent(title)}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Delete failed');

        await fetchAllBooks();
        showToast('Book deleted successfully', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error deleting book', 'error');
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('bookModal');
    if (event.target === modal) {
        closeModal();
    }
}
