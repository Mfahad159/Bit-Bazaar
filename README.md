# Bit Bazaar - Game Store API and Frontend

Bit Bazaar is a full-stack application for managing an online game store. It provides a backend API for managing games, users, orders, and payments, along with a frontend for user interaction. The project is designed to simulate an e-commerce platform with features like game inventory management, user authentication, cart functionality, and admin controls.

---

## Project Overview

The GameStore API provides functionalities to simulate an e-commerce platform for video games. Key features include:
* Game inventory management (CRUD operations for games).
* User account management (to be implemented).
* Order processing (to be implemented).
* Payment simulation (to be implemented).

## Technology Stack

- **Backend**: Python with FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Database**: Microsoft SQL Server
- **ORM**: SQLAlchemy
- **Server**: Uvicorn

---

## Current Functionality (As of May 8, 2025)

* **Database Schema:**
    * Tables for `Users`, `Games`, `Orders`, `OrderItems`, and `Payments` have been designed and created in SQL Server.
    * Relationships, primary keys, foreign keys, and basic constraints are established.
    * Triggers for automatically updating `updated_at` timestamps on `Games` and `Orders` tables.
* **FastAPI Backend:**
    * Basic application structure is set up.
    * Database connection to SQL Server is configured using SQLAlchemy and `pyodbc`.
    * SQLAlchemy models (currently for `Game`) are defined.
    * Pydantic schemas for request/response validation (currently for `Game`) are defined.
* **API Endpoints:**
    * **Games CRUD:**
        * `POST /games/`: Create a new game. (Verified Working)
        * `GET /games/`: Retrieve a list of games. (Testing in progress)
        * `GET /games/{game_id}`: Retrieve a specific game by ID. (Testing in progress)
        * `PUT /games/{game_id}`: Update an existing game. (Code present)
        * `DELETE /games/{game_id}`: Delete a game. (Code present)
    * Interactive API documentation available via `/docs` (Swagger UI) and `/redoc`.

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
