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
        const response = await fetch('http://localhost:8000/games/');
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

    try {
        const response = await fetch('http://localhost:8000/cart/add', {
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
