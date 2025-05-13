document.getElementById('addGameForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login as an admin to add games.');
        window.location.href = 'login.html';
        return;
    }

    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const price = parseFloat(document.getElementById('price').value);
    const genre = document.getElementById('genre').value;
    const image_url = document.getElementById('image_url').value;

    try {
        const response = await fetch('http://localhost:8000/api/games/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ title, description, price, genre, image_url })
        });

        if (response.ok) {
            alert('Game added successfully!');
            document.getElementById('addGameForm').reset();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to add game.');
        }
    } catch (error) {
        console.error('Error adding game:', error);
        alert('An error occurred. Please try again.');
    }
});
