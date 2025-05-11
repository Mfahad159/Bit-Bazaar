// Cart state
let cartItems = [];
let cartTotal = 0;

// DOM Elements
const cartItemsContainer = document.getElementById('cartItems');
const cartTotalElement = document.getElementById('cartTotal');
const checkoutBtn = document.getElementById('checkoutBtn');

// Fetch cart items from backend
// Fetch cart items from the backend
async function fetchCart() {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login to view your cart');
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/api/cart/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const cartItems = await response.json();
            displayCartItems(cartItems);
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to fetch cart items');
        }
    } catch (error) {
        console.error('Error fetching cart:', error);
        alert('Failed to fetch cart items. Please try again.');
    }
}

async function addToCart(gameId) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login to add items to cart');
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/api/cart/add', {
            method: 'POST', // Ensure this is POST
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                game_id: gameId,
                quantity: 1
            })
        });

        if (response.ok) {
            alert('Game added to cart!');
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to add game to cart');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Failed to add game to cart. Please try again.');
    }
}

// Display cart items and total price
function displayCartItems(cartItems) {
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotalElement = document.getElementById('cartTotal');

    if (cartItems.length === 0) {
        cartItemsContainer.innerHTML = '<p>Your cart is empty</p>';
        cartTotalElement.textContent = '$0.00';
        return;
    }

    let totalPrice = 0;
    cartItemsContainer.innerHTML = '';
    cartItems.forEach(item => {
        const itemTotal = item.game.price * item.quantity;
        totalPrice += itemTotal;

        const cartItemElement = document.createElement('div');
        cartItemElement.className = 'cart-item';
        cartItemElement.innerHTML = `
            <div>
                <h3>${item.game.title}</h3>
                <p>Price: $${item.game.price.toFixed(2)}</p>
                <p>Quantity: ${item.quantity}</p>
                <p>Total: $${itemTotal.toFixed(2)}</p>
            </div>
        `;
        cartItemsContainer.appendChild(cartItemElement);
    });

    cartTotalElement.textContent = `$${totalPrice.toFixed(2)}`;
}

// Initialize cart on page load
document.addEventListener('DOMContentLoaded', fetchCart);

// Update cart display
function updateCartDisplay(items) {
    cartItems = items;
    cartItemsContainer.innerHTML = '';
    
    if (items.length === 0) {
        cartItemsContainer.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        cartTotalElement.textContent = '$0.00';
        checkoutBtn.disabled = true;
        return;
    }

    let total = 0;
    items.forEach(item => {
        const itemTotal = item.game.price * item.quantity;
        total += itemTotal;

        const itemElement = document.createElement('div');
        itemElement.className = 'cart-item';
        itemElement.innerHTML = `
            <div class="item-info">
                <img src="${item.game.image_url}" alt="${item.game.title}" class="item-image">
                <div class="item-details">
                    <h3>${item.game.title}</h3>
                    <p class="item-price">$${item.game.price.toFixed(2)}</p>
                </div>
            </div>
            <div class="item-quantity">
                <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                <span>${item.quantity}</span>
                <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
            </div>
            <div class="item-total">
                $${itemTotal.toFixed(2)}
            </div>
            <button class="remove-item" onclick="removeItem(${item.id})">
                <i class="fas fa-trash"></i>
            </button>
        `;
        cartItemsContainer.appendChild(itemElement);
    });

    cartTotal = total;
    cartTotalElement.textContent = `$${total.toFixed(2)}`;
    checkoutBtn.disabled = false;
}

// Update quantity
async function updateQuantity(itemId, newQuantity) {
    if (newQuantity < 1) return;
    
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`/api/cart/items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ quantity: newQuantity })
        });

        if (!response.ok) throw new Error('Failed to update quantity');
        
        // Refresh cart after update
        fetchCart();
    } catch (error) {
        console.error('Error updating quantity:', error);
        alert('Failed to update quantity. Please try again.');
    }
}

// Remove item
async function removeItem(itemId) {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`/api/cart/items/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to remove item');
        
        // Refresh cart after removal
        fetchCart();
    } catch (error) {
        console.error('Error removing item:', error);
        alert('Failed to remove item. Please try again.');
    }
}

// Initialize cart
document.addEventListener('DOMContentLoaded', fetchCart);

// Handle checkout
document.getElementById('checkoutBtn').addEventListener('click', async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login to proceed with checkout');
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch('/api/orders/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                items: cartItems.map(item => ({
                    game_id: item.game.id,
                    quantity: item.quantity
                }))
            })
        });

        if (!response.ok) throw new Error('Checkout failed');

        alert('Order placed successfully!');
        fetchCart(); // Refresh cart (should be empty after successful order)
    } catch (error) {
        console.error('Error during checkout:', error);
        alert('Checkout failed. Please try again.');
    }
});
