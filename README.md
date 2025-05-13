# Bit Bazaar - Game Store API and Frontend

Bit Bazaar is a full-stack application for managing an online game store. It provides a backend API for managing games, users, orders, and payments, along with a frontend for user interaction. The project is designed to simulate an e-commerce platform with features like game inventory management, user authentication, cart functionality, and admin controls.

---

## Project Overview

Bit Bazaar offers the following key features:

### Backend
- **Game Inventory Management**: CRUD operations for games.
- **User Authentication**: Secure login and registration with role-based access (admin and customer).
- **Cart Management**: Add, update, and remove items from the cart.
- **Order Processing**: Convert cart items into orders and simulate payments.
- **Admin Panel**: Manage games and track inventory.

### Frontend
- **Game Display**: Browse games with filtering by category.
- **Cart Functionality**: Add games to the cart and view the total price.
- **Admin Dashboard**: Add, edit, and delete games from the inventory.

---

## Technology Stack

- **Backend**: Python with FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Database**: Microsoft SQL Server
- **ORM**: SQLAlchemy
- **Server**: Uvicorn

---

## Current Functionality

### Database Schema
- Tables for `Users`, `Games`, `Orders`, `OrderItems`, `CartItems`, and `Payments` have been designed and implemented in SQL Server.
- Relationships, primary keys, foreign keys, and constraints are established.
- Triggers for automatically updating `updated_at` timestamps on `Games` and `Orders` tables.

### Backend
- **Authentication**:
  - Secure login and registration with hashed passwords.
  - Role-based access control (admin and customer).
  - JWT-based authentication for API endpoints.
- **Game Management**:
  - Create a new game (admin only).
  - Retrieve a list of games.
  - Retrieve a specific game by ID.
  - Update an existing game (admin only).
  - Delete a game (admin only).
- **Cart Management**:
  - Add an item to the cart.
  - Retrieve all items in the user's cart.
  - Update the quantity of a cart item.
  - Remove an item from the cart.
  - Convert cart items into an order.
- **Order Management**:
  - Create a new order.
  - Retrieve all orders for the logged-in user.
  - Retrieve a specific order by ID.
- **Payment Simulation**:
  - Process a payment for an order.

### Frontend
- **User Authentication**:
  - Login and registration pages with role selection (admin or customer).
  - Dynamic navigation links based on authentication status.
- **Game Display**:
  - Browse games in a grid format with filtering by category.
  - Add games to the cart with real-time updates to the cart count.
- **Cart**:
  - View cart items with options to update quantities or remove items.
  - Proceed to checkout and simulate order placement.
- **Admin Panel**:
  - Add new games to the inventory.
  - Edit or delete existing games.
  - View total games in the inventory.

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- Microsoft SQL Server (ensure an instance is running, e.g., SQLEXPRESS)
- SQL Server Management Studio (SSMS) or a similar tool to manage the database.
- Git

### Steps

1. **Clone the Repository**:
    ```bash
    git clone <your-repository-url>
    cd Bit-Bazaar
    ```

2. **Create and Activate Virtual Environment**:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Database Setup**:
    - Open SSMS and connect to your SQL Server instance.
    - Create a new database named `GameStoreDB`.
    - Ensure the tables (`Users`, `Games`, `Orders`, `OrderItems`, `CartItems`, `Payments`) are created. You can use SQLAlchemy's `Base.metadata.create_all(bind=engine)` in `backend/database.py` for automatic table creation.

5. **Configure Database Connection**:
    - Open the `backend/database.py` file.
    - Update the `SERVER_NAME` variable with your SQL Server instance name (e.g., `r"YourComputerName\SQLEXPRESS"` or `r"(localdb)\MSSQLLocalDB"`).
    - Ensure the `DATABASE_NAME` is `GameStoreDB`.
    - Verify the ODBC driver version if necessary (default is `ODBC Driver 17 for SQL Server`).

6. **Run the Backend**:
    ```bash
    uvicorn backend.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

7. **Run the Frontend**:
    - Open the `frontend/index.html` file in a browser.
    - Ensure the backend is running to fetch and display games.

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## Project Structure

```
Bit-Bazaar/
├── backend/
│   ├── __init__.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── static/
│       ├── images/
│       └── js/
├── frontend/
│   ├── admin.html
│   ├── cart.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── css/
│   │   ├── auth.css
│   │   ├── cart.css
│   │   ├── style.css
│   ├── js/
│   │   ├── admin.js
│   │   ├── auth.js
│   │   ├── cart.js
│   │   ├── games.js
├── requirements.txt
├── README.md
```

---

## Future Enhancements

- **Order Tracking**: Add order status updates (e.g., shipped, delivered).
- **Payment Gateway Integration**: Replace simulated payments with real payment processing.
- **User Profiles**: Allow users to update their profile information.
- **Enhanced Admin Panel**: Add analytics and sales tracking.
- **Responsive Design**: Improve mobile compatibility for the frontend.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contributors

- **Your Name** - Developer
- **Your Team Members** (if applicable)

Feel free to contribute to this project by submitting issues or pull requests.
