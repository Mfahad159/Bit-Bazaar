// Cart state
let cartItems = [];
let cartTotal = 0;

// DOM Elements
const cartItemsContainer = document.getElementById('cart-items');
const cartTotalElement = document.getElementById('cart-total-amount');
const checkoutBtn = document.getElementById('checkout-btn');

// Fetch cart items from backend
async function fetchCart() {
    const token = localStorage.getItem('token');
    if (!token) {
        showMessage('Please login to view your cart', 'error');
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch('/api/cart/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const items = await response.json();
            displayCartItems(items);
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Failed to fetch cart items', 'error');
        }
    } catch (error) {
        console.error('Error fetching cart:', error);
        showMessage('Failed to fetch cart items. Please try again.', 'error');
    }
}

// Add to cart functionality
async function addToCart(gameId) {
    const token = localStorage.getItem('token');
    if (!token) {
        showMessage('Please login to add items to cart', 'error');
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
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
            showMessage('Game added to cart successfully!', 'success');
            fetchCart(); // Refresh cart after adding item
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Failed to add game to cart', 'error');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showMessage('Failed to add game to cart. Please try again.', 'error');
    }
}

// Update cart display
function displayCartItems(items) {
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
        itemElement.setAttribute('data-cart-item-id', item.id);
        
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
            <button class="remove-item" onclick="removeFromCart(${item.id})">
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
    if (!token) {
        showMessage('Please login to update cart', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/cart/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ quantity: newQuantity })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update quantity');
        }
        
        showMessage('Quantity updated successfully', 'success');
        fetchCart(); // Refresh cart after update
    } catch (error) {
        console.error('Error updating quantity:', error);
        showMessage(error.message || 'Failed to update quantity', 'error');
    }
}

// Remove item
async function removeFromCart(itemId) {
    const token = localStorage.getItem('token');
    if (!token) {
        showMessage('Please login to remove items', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/cart/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to remove item');
        }
        
        showMessage('Item removed successfully', 'success');
        fetchCart(); // Refresh cart after removal
    } catch (error) {
        console.error('Error removing item:', error);
        showMessage(error.message || 'Failed to remove item', 'error');
    }
}

// Handle checkout
async function proceedToCheckout() {
    const token = localStorage.getItem('token');
    if (!token) {
        showMessage('Please login to proceed with checkout', 'error');
        window.location.href = 'login.html';
        return;
    }

    try {
        // First create the order
        const orderResponse = await fetch('/api/cart/checkout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!orderResponse.ok) {
            const errorData = await orderResponse.json();
            throw new Error(errorData.detail || 'Failed to create order');
        }

        const order = await orderResponse.json();

        // Then create the payment
        const paymentResponse = await fetch('/api/payments/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                order_id: order.order_id,
                amount_paid: parseFloat(order.total_price),
                payment_method: 'credit_card',
                payment_status: 'Pending'
            })
        });

        if (!paymentResponse.ok) {
            const errorData = await paymentResponse.json();
            throw new Error(errorData.detail || 'Failed to process payment');
        }

        showMessage('Order placed successfully!', 'success');
        
        // Clear the cart display
        cartItemsContainer.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        cartTotalElement.textContent = '$0.00';
        checkoutBtn.disabled = true;

        // Redirect to orders page
        setTimeout(() => {
            window.location.href = '/orders.html';
        }, 2000);

    } catch (error) {
        console.error('Error during checkout:', error);
        showMessage(error.message || 'Failed to complete checkout', 'error');
    }
}

function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // Remove message after 3 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Initialize cart
document.addEventListener('DOMContentLoaded', fetchCart);
