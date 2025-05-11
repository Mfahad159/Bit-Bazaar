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
        const response = await fetch('/api/games/');
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
        : games.filter(game => game.category === category);
    displayGames(filteredGames);
}

// Display games in the grid
function displayGames(gamesToShow) {
    gamesGrid.innerHTML = '';
    gamesToShow.forEach(game => {
        const gameCard = document.createElement('div');
        gameCard.className = 'game-card';
        gameCard.innerHTML = `
            <img src="${game.image}" alt="${game.title}" class="game-image">
            <div class="game-info">
                <h3 class="game-title">${game.title}</h3>
                <p class="game-price">$${game.price}</p>
                <button class="add-to-cart" onclick="addToCart(${game.id})">
                    Add to Cart
                </button>
            </div>
        `;
        gamesGrid.appendChild(gameCard);
    });
}

// Add to cart functionality
async function addToCart(gameId) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login to add items to cart');
        window.location.href = 'login.html';
        return;
    }

    const addButton = event.target;
    const originalText = addButton.textContent;
    addButton.textContent = 'Adding...';
    addButton.disabled = true;

    try {
        const response = await fetch('/api/cart/items/', {
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
            const successMessage = document.createElement('div');
            successMessage.className = 'success-message';
            successMessage.textContent = 'Added to cart!';
            document.body.appendChild(successMessage);
            
            setTimeout(() => {
                successMessage.remove();
                addButton.textContent = originalText;
                addButton.disabled = false;
            }, 2000);

            // Update cart count in nav
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
            alert(error.detail || 'Failed to add game to cart');
            addButton.textContent = originalText;
            addButton.disabled = false;
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Failed to add game to cart. Please try again.');
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

// Initial display
document.addEventListener('DOMContentLoaded', () => {
    fetchGames();
});
