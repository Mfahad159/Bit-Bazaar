// Store games data
let games = [];

// DOM Elements
const gamesGrid = document.getElementById('gamesGrid');
const categoryFilters = document.getElementById('categoryFilters');

// Current filter
let currentFilter = 'all';

// Fetch games from API
async function fetchGames() {
    try {
        const response = await fetch('api/games/');
        if (!response.ok) throw new Error('Failed to fetch games');
        games = await response.json();
        displayGames(games);
    } catch (error) {
        console.error('Error fetching games:', error);
        alert('Failed to load games. Please try again later.');
    }
}

// Filter games by category
function filterGames(category) {
    currentFilter = category;
    const filteredGames = category === 'all' 
        ? games 
        : games.filter(game => game.genre === category);
    displayGames(filteredGames);
}

// Display games in the grid
function displayGames(gamesToShow) {
    gamesGrid.innerHTML = '';
    gamesToShow.forEach(game => {
        const gameCard = document.createElement('div');
        gameCard.className = 'game-card';
        gameCard.innerHTML = `
            <img src="${game.image_url}" 
                 alt="${game.title}" 
                 class="game-image"
                 onerror="this.src='https://placehold.co/200x200/1a1a1a/ffffff?text=No+Image'">
            <div class="game-info">
                <h3 class="game-title">${game.title}</h3>
                <p class="game-description">${game.description}</p>
                <p class="game-price">$${game.price.toFixed(2)}</p>
                <button class="add-to-cart" onclick="addToCart(${game.game_id}, event)">
                    Add to Cart
                </button>
            </div>
        `;
        gamesGrid.appendChild(gameCard);
    });
}

// Add to cart functionality
async function addToCart(gameId, event) {
    const token = localStorage.getItem('token');
    if (!token) {
        showMessage('Please login to add items to cart', 'error');
        window.location.href = 'login.html';
        return;
    }

    const addButton = event.target;
    const originalText = addButton.textContent;
    addButton.textContent = 'Adding...';
    addButton.disabled = true;

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
            
            // Update cart count
            const cartResponse = await fetch('/api/cart/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (cartResponse.ok) {
                const cartData = await cartResponse.json();
                const cartCount = cartData.reduce((total, item) => total + item.quantity, 0);
                updateCartCount(cartCount);
            }
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Failed to add game to cart', 'error');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showMessage('Failed to add game to cart. Please try again.', 'error');
    } finally {
        // Reset button state
        addButton.textContent = originalText;
        addButton.disabled = false;
    }
}

// Update cart count in navigation
function updateCartCount(count) {
    const cartLink = document.querySelector('.nav-links a[href="cart.html"]');
    if (cartLink) {
        const badge = cartLink.querySelector('.cart-badge') || document.createElement('span');
        badge.className = 'cart-badge';
        badge.textContent = count;
        if (count > 0) {
            cartLink.appendChild(badge);
        } else {
            badge.remove();
        }
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchGames();
    if (categoryFilters) {
        categoryFilters.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                // Update active button
                document.querySelectorAll('.filter-btn').forEach(btn => 
                    btn.classList.remove('active'));
                e.target.classList.add('active');
                
                // Filter games
                filterGames(e.target.dataset.category);
            }
        });
    }
});
