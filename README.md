# GameStore API

This project is a backend API for an online Game Store, developed as part of the Database Systems course. It allows for managing games, users, orders, and more, with a focus on database interactions and SQL.

## Project Overview

The GameStore API provides functionalities to simulate an e-commerce platform for video games. Key features include:
* Game inventory management (CRUD operations for games).
* User account management (to be implemented).
* Order processing (to be implemented).
* Payment simulation (to be implemented).
* Frontend integration for displaying games and managing the cart.

## Technology Stack

* **Backend:** Python with FastAPI
* **Frontend:** HTML, CSS, JavaScript
* **Database:** Microsoft SQL Server
* **ORM:** SQLAlchemy
* **Server:** Uvicorn

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
        * `GET /games/`: Retrieve a list of games. (Verified Working)
        * `GET /games/{game_id}`: Retrieve a specific game by ID. (Verified Working)
        * `PUT /games/{game_id}`: Update an existing game. (Verified Working)
        * `DELETE /games/{game_id}`: Delete a game. (Verified Working)
    * **Cart Management:**
        * `POST /cart/items/`: Add an item to the cart. (Verified Working)
        * `GET /cart/`: Retrieve cart items. (Verified Working)
* **Frontend Integration:**
    * Display games in a grid format with filtering by category.
    * Add games to the cart with real-time updates to the cart count.
    * User authentication for cart operations.

## Setup and Installation

1.  **Prerequisites:**
    * Python 3.10+
    * Microsoft SQL Server (ensure an instance is running, e.g., SQLEXPRESS)
    * SQL Server Management Studio (SSMS) or a similar tool to manage the database.
    * Git

2.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd Bit-Bazaar
    ```

3.  **Create and Activate Virtual Environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Database Setup:**
    * Open SSMS and connect to your SQL Server instance.
    * Create a new database named `GameStoreDB`.
    * The tables (`Users`, `Games`, `Orders`, `OrderItems`, `Payments`) are defined in SQL scripts that should be run against `GameStoreDB`. (You might want to save your `CREATE TABLE` scripts into a `.sql` file in the repository, e.g., `database_schema.sql`, and mention it here).
        * *Alternatively, if you decide to use SQLAlchemy for table creation (not current approach), you would run a script or have `models.Base.metadata.create_all(bind=engine)` in `main.py` uncommented for the initial setup.*

6.  **Configure Database Connection:**
    * Open the `backend/database.py` file.
    * Locate the `SERVER_NAME` variable.
    * Update it with your SQL Server instance name (e.g., `r"YourComputerName\SQLEXPRESS"` or `r"(localdb)\MSSQLLocalDB"`).
    * Ensure the `DATABASE_NAME` is `GameStoreDB`.
    * Verify the ODBC driver version if necessary (default is `ODBC Driver 17 for SQL Server`).

7.  **Run the Application:**
    * Ensure your terminal is in the project root directory (`Bit-Bazaar`).
    * Run Uvicorn:
        ```bash
        uvicorn backend.main:app --reload
        ```
    * The API will be available at `http://127.0.0.1:8000`.

8.  **Frontend Setup:**
    * Open the `index.html` file in the `frontend` directory in a browser.
    * Ensure the backend is running to fetch and display games.

## API Documentation

Once the application is running, interactive API documentation can be accessed at:
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`
