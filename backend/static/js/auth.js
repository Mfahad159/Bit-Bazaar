// Check authentication status
async function checkAuth() {
    const token = localStorage.getItem('token');
    
    if (!token) return false;

    try {
        const response = await fetch('/api/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            updateAuthUI(user);
            return true;
        } else {
            // Token is invalid or expired
            localStorage.removeItem('token');
            return false;
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        return false;
    }
}

// Update UI based on authentication status
function updateAuthUI(user) {
    const authLinks = document.getElementById('authLinks');
    if (user) {
        authLinks.innerHTML = `
            <span>Welcome, ${user.username}</span>
            <a href="#" onclick="logout()">Logout</a>
            ${user.is_admin ? '<a href="admin.html">Admin Panel</a>' : ''}
        `;
    } else {
        authLinks.innerHTML = `
            <a href="login.html">Login</a>
            <a href="register.html">Register</a>
        `;
    }
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
}

// Check auth status on page load
document.addEventListener('DOMContentLoaded', checkAuth);
