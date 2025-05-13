// DOM Elements
const gamesList = document.getElementById('gamesList');
const addGameForm = document.getElementById('addGameForm');
const editGameForm = document.getElementById('editGameForm');
const editGameModal = document.getElementById('editGameModal');

// Store games data
let games = [];

// Check if user is admin
async function checkAdmin() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }

    try {
        const response = await fetch('api/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            return user.role === 'admin';
        }
        return false;
    } catch (error) {
        console.error('Admin check failed:', error);
        return false;
    }
}

// Fetch all games
async function fetchGames() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('api/games/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch games');
        games = await response.json();
        displayGames();
        updateAdminStats();
    } catch (error) {
        console.error('Error fetching games:', error);
        alert('Failed to load games. Please try again later.');
    }
}

// Display games in the list
function displayGames() {
    gamesList.innerHTML = '';
    games.forEach(game => {
        const gameElement = document.createElement('div');
        gameElement.className = 'game-item';
        gameElement.innerHTML = `
            <img src="${game.image_url}" 
                 alt="${game.title}" 
                 class="game-image"
                 onerror="this.src='https://placehold.co/120x120/1a1a1a/ffffff?text=No+Image'">
            <div class="game-info">
                <h3>${game.title}</h3>
                <p class="game-description">${game.description}</p>
                <p class="game-price">Price: $${game.price.toFixed(2)}</p>
                <p class="game-genre">Genre: ${game.genre}</p>
                <p class="game-stock">Stock: ${game.stock_quantity}</p>
            </div>
            <div class="game-actions">
                <button onclick="editGame(${game.game_id})" class="edit-btn">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button onclick="deleteGame(${game.game_id})" class="delete-btn">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        `;
        gamesList.appendChild(gameElement);
    });
}

// Add new game
async function addGame(event) {
    event.preventDefault();
    const token = localStorage.getItem('token');
    const formData = new FormData(addGameForm);
    const gameData = {
        title: formData.get('title'),
        description: formData.get('description'),
        price: parseFloat(formData.get('price')),
        genre: formData.get('genre'),
        stock_quantity: parseInt(formData.get('stock_quantity')),
        image_url: formData.get('image_url')
    };

    try {
        const response = await fetch('api/games/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(gameData)
        });

        if (response.ok) {
            const successMessage = document.createElement('div');
            successMessage.className = 'success-message';
            successMessage.textContent = 'Game added successfully!';
            document.body.appendChild(successMessage);
            
            setTimeout(() => {
                successMessage.remove();
            }, 2000);

            addGameForm.reset();
            fetchGames();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to add game');
        }
    } catch (error) {
        console.error('Error adding game:', error);
        alert('Failed to add game. Please try again.');
    }
}

// Edit game
async function editGame(gameId) {
    const game = games.find(g => g.game_id === gameId);
    if (!game) return;

    openEditModal(game);
}

// Open the edit modal
function openEditModal(game) {
    const modal = document.getElementById('editGameModal');
    modal.classList.add('show');

    // Populate the form with game data
    document.getElementById('editGameId').value = game.game_id;
    document.getElementById('editTitle').value = game.title;
    document.getElementById('editDescription').value = game.description;
    document.getElementById('editPrice').value = game.price;
    document.getElementById('editGenre').value = game.genre;
    document.getElementById('editStockQuantity').value = game.stock_quantity;
    document.getElementById('editImageUrl').value = game.image_url;
}

// Close the edit modal
function closeEditModal() {
    const modal = document.getElementById('editGameModal');
    modal.classList.remove('show');
}

// Update game
async function updateGame(event) {
    event.preventDefault();
    const token = localStorage.getItem('token');
    const formData = new FormData(editGameForm);
    const gameId = formData.get('gameId');
    const gameData = {
        title: formData.get('title'),
        description: formData.get('description'),
        price: parseFloat(formData.get('price')),
        genre: formData.get('genre'),
        stock_quantity: parseInt(formData.get('stock_quantity')),
        image_url: formData.get('image_url')
    };

    try {
        const response = await fetch(`api/games/${gameId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(gameData)
        });

        if (response.ok) {
            const successMessage = document.createElement('div');
            successMessage.className = 'success-message';
            successMessage.textContent = 'Game updated successfully!';
            document.body.appendChild(successMessage);
            
            setTimeout(() => {
                successMessage.remove();
            }, 2000);

            closeEditModal();
            fetchGames();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to update game');
        }
    } catch (error) {
        console.error('Error updating game:', error);
        alert('Failed to update game. Please try again.');
    }
}

// Delete game
async function deleteGame(gameId) {
    if (!confirm('Are you sure you want to delete this game?')) return;

    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`api/games/${gameId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const successMessage = document.createElement('div');
            successMessage.className = 'success-message';
            successMessage.textContent = 'Game deleted successfully!';
            document.body.appendChild(successMessage);
            
            setTimeout(() => {
                successMessage.remove();
            }, 2000);

            fetchGames();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to delete game');
        }
    } catch (error) {
        console.error('Error deleting game:', error);
        alert('Failed to delete game. Please try again.');
    }
}

// Close modal when clicking outside the modal content
window.addEventListener('click', (event) => {
    const modal = document.getElementById('editGameModal');
    if (event.target === modal) {
        closeEditModal();
    }
});

// Update admin stats
async function updateAdminStats() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        // Fetch total games
        const gamesResponse = await fetch('api/games/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (gamesResponse.ok) {
            const games = await gamesResponse.json();
            document.getElementById('totalGames').textContent = games.length;
        }
    } catch (error) {
        console.error('Error fetching admin stats:', error);
    }
}

// Initialize admin panel
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Check if user is admin
    const isAdmin = await checkAdmin();
    if (!isAdmin) {
        alert('Access denied. Admin privileges required.');
        window.location.href = 'index.html';
        return;
    }

    // Initialize forms
    addGameForm.addEventListener('submit', addGame);
    editGameForm.addEventListener('submit', updateGame);

    // Initial load
    fetchGames();
});