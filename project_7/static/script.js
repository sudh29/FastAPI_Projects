const API_URL = ''; // Relative path
let credentials = null;

// DOM Elements
const app = document.getElementById('app');
const loginScreen = document.getElementById('login-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const loginForm = document.getElementById('login-form');
const productGrid = document.getElementById('product-grid');
const modalOverlay = document.getElementById('modal-overlay');
const productForm = document.getElementById('product-form');
const addProductBtn = document.getElementById('add-product-btn');
const cancelBtn = document.getElementById('cancel-btn');
const logoutBtn = document.getElementById('logout-btn');
const toast = document.getElementById('toast');

// State
let products = [];
let isEditing = false;

// Init
function init() {
    const storedCreds = localStorage.getItem('auth');
    if (storedCreds) {
        credentials = storedCreds;
        showDashboard();
    } else {
        showLogin();
    }
}

// Navigation
function showLogin() {
    loginScreen.classList.add('active');
    dashboardScreen.classList.remove('active');
}

function showDashboard() {
    loginScreen.classList.remove('active');
    dashboardScreen.classList.add('active');
    fetchProducts();
}

// Auth
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;
    const creds = btoa(`${username}:${password}`);

    // Verify credentials by fetching products
    try {
        const res = await fetch(`${API_URL}/products`, {
            headers: { 'Authorization': `Basic ${creds}` }
        });

        if (res.ok) {
            credentials = creds;
            localStorage.setItem('auth', creds);
            showDashboard();
            showToast('Welcome back!');
        } else {
            showToast('Invalid credentials');
        }
    } catch (err) {
        showToast('Connection error');
    }
});

logoutBtn.addEventListener('click', () => {
    credentials = null;
    localStorage.removeItem('auth');
    showLogin();
});

// API Calls
async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
    };

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(`${API_URL}${endpoint}`, options);

    if (res.status === 401) {
        logoutBtn.click();
        throw new Error('Unauthorized');
    }

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'API Error');
    }

    if (res.status === 204) return null;
    return res.json();
}

async function fetchProducts() {
    try {
        products = await apiCall('/products');
        renderProducts();
    } catch (err) {
        showToast(err.message);
    }
}

// Rendering
function renderProducts() {
    productGrid.innerHTML = products.map(p => `
        <div class="glass-panel product-card">
            <div class="product-header">
                <div class="product-name">${p.name}</div>
                <div class="product-price">$${p.price.toFixed(2)}</div>
            </div>
            <div class="product-desc">${p.description || 'No description'}</div>
            <div class="product-meta" style="margin-bottom: 1rem; color: #cbd5e1; font-size: 0.9rem;">
                Quantity: <span id="qty-${p.id}">${p.quantity}</span>
                <div class="inventory-controls" style="display: inline-flex; gap: 5px; margin-left: 10px;">
                    <button class="btn-secondary" style="padding: 2px 8px;" onclick="updateInventory(${p.id}, -1)">-</button>
                    <button class="btn-secondary" style="padding: 2px 8px;" onclick="updateInventory(${p.id}, 1)">+</button>
                </div>
            </div>
            <div class="product-actions">
                <button class="btn-edit" onclick="editProduct(${p.id})">Edit</button>
                <button class="btn-danger" onclick="deleteProduct(${p.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Modal
function showModal(title) {
    document.getElementById('modal-title').innerText = title;
    modalOverlay.classList.remove('hidden');
}

function hideModal() {
    modalOverlay.classList.add('hidden');
    productForm.reset();
    isEditing = false;
}

addProductBtn.addEventListener('click', () => {
    isEditing = false;
    document.getElementById('prod-id').disabled = false;
    showModal('Add Product');
});

cancelBtn.addEventListener('click', hideModal);

// Forms
window.editProduct = (id) => {
    const p = products.find(x => x.id === id);
    if (!p) return;

    isEditing = true;
    document.getElementById('prod-id-hidden').value = p.id;
    document.getElementById('prod-id').value = p.id;
    document.getElementById('prod-id').disabled = true; // Cannot change ID
    document.getElementById('prod-name').value = p.name;
    document.getElementById('prod-price').value = p.price;
    document.getElementById('prod-desc').value = p.description || '';
    document.getElementById('prod-qty').value = p.quantity;

    showModal('Edit Product');
};

window.deleteProduct = async (id) => {
    if (!confirm('Are you sure?')) return;
    try {
        await apiCall(`/products/${id}`, 'DELETE');
        showToast('Product deleted');
        fetchProducts();
    } catch (err) {
        showToast(err.message);
    }
};

window.updateInventory = async (id, delta) => {
    try {
        await apiCall(`/products/${id}/inventory`, 'PATCH', { delta });
        // Optimistic update or refetch
        fetchProducts();
        showToast('Inventory updated');
    } catch (err) {
        showToast(err.message);
    }
};

productForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const product = {
        id: parseInt(document.getElementById('prod-id').value),
        name: document.getElementById('prod-name').value,
        price: parseFloat(document.getElementById('prod-price').value),
        description: document.getElementById('prod-desc').value,
        quantity: parseInt(document.getElementById('prod-qty').value)
    };

    try {
        if (isEditing) {
            await apiCall(`/products/${product.id}`, 'PUT', product);
            showToast('Product updated');
        } else {
            await apiCall('/products', 'POST', product);
            showToast('Product created');
        }
        hideModal();
        fetchProducts();
    } catch (err) {
        showToast(err.message);
    }
});

// Toast
function showToast(msg) {
    toast.innerText = msg;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

init();
