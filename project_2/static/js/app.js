const API_URL = '/books';

document.addEventListener('DOMContentLoaded', () => {
    fetchBooks();
    setupEventListeners();
});

function setupEventListeners() {
    // Add Book Form
    document.getElementById('add-book-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const book = {
            title: formData.get('title'),
            author: formData.get('author'),
            description: formData.get('description'),
            rating: parseInt(formData.get('rating')),
            published_date: parseInt(formData.get('published_date'))
        };

        try {
            const response = await fetch('/create-book', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(book)
            });

            if (response.ok) {
                e.target.reset();
                fetchBooks();
            } else {
                alert('Failed to add book');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Filter
    document.getElementById('rating-filter').addEventListener('change', (e) => {
        fetchBooks(e.target.value);
    });

    // Refresh
    document.getElementById('refresh-btn').addEventListener('click', () => {
        fetchBooks(document.getElementById('rating-filter').value);
    });

    // Edit Modal Close
    document.querySelector('.close').addEventListener('click', () => {
        document.getElementById('edit-modal').style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target == document.getElementById('edit-modal')) {
            document.getElementById('edit-modal').style.display = 'none';
        }
    });

    // Edit Form Submit
    document.getElementById('edit-book-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const book = {
            id: parseInt(formData.get('id')),
            title: formData.get('title'),
            author: formData.get('author'),
            description: formData.get('description'),
            rating: parseInt(formData.get('rating')),
            published_date: parseInt(formData.get('published_date'))
        };

        try {
            const response = await fetch('/books/update_book', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(book)
            });

            if (response.ok) {
                document.getElementById('edit-modal').style.display = 'none';
                fetchBooks();
            } else {
                alert('Failed to update book');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
}

async function fetchBooks(rating = '') {
    let url = API_URL;
    if (rating) {
        url += `?rating=${rating}`;
    }

    try {
        const response = await fetch(url);
        const books = await response.json();
        renderBooks(books);
    } catch (error) {
        console.error('Error fetching books:', error);
    }
}

function renderBooks(books) {
    const container = document.getElementById('books-container');
    container.innerHTML = '';

    books.forEach(book => {
        const card = document.createElement('div');
        card.className = 'book-card';
        card.innerHTML = `
            <h3>${book.title}</h3>
            <div class="author">by ${book.author}</div>
            <div class="details">${book.description}</div>
            <div class="meta">
                <span class="rating">${'★'.repeat(book.rating)}${'☆'.repeat(5 - book.rating)}</span>
                <span class="year">${book.published_date}</span>
            </div>
            <div class="card-actions">
                <button class="btn-small btn-edit" onclick="openEditModal(${book.id})">Edit</button>
                <button class="btn-small btn-delete" onclick="deleteBook(${book.id})">Delete</button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function deleteBook(id) {
    if (!confirm('Are you sure you want to delete this book?')) return;

    try {
        const response = await fetch(`/books/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            fetchBooks();
        } else {
            alert('Failed to delete book');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function openEditModal(id) {
    try {
        const response = await fetch(`/books/${id}`);
        const book = await response.json();

        document.getElementById('edit-id').value = book.id;
        document.getElementById('edit-title').value = book.title;
        document.getElementById('edit-author').value = book.author;
        document.getElementById('edit-description').value = book.description;
        document.getElementById('edit-rating').value = book.rating;
        document.getElementById('edit-published_date').value = book.published_date;

        document.getElementById('edit-modal').style.display = 'flex';
    } catch (error) {
        console.error('Error fetching book details:', error);
    }
}
