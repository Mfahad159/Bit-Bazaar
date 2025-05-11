from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 
from sqlalchemy.orm import sessionmaker
import urllib    # Required for pyodbc connection string
import os
from sqlalchemy.exc import SQLAlchemyError
#==============================================================================
# Database Configuration
#==============================================================================

# SQL Server Connection String - preferably from environment variables
SERVER_NAME = os.getenv('DB_SERVER', r"DESKTOP-EC65IMO\SQLEXPRESS") 
DATABASE_NAME = os.getenv('DB_NAME', "GAMESTOREDB") 

# For Windows Authentication (most common for local dev SQL Server Express)
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;" # Use Windows Authentication
)
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# print(f"Attempting to connect to: {SQLALCHEMY_DATABASE_URL}")
# try:
#     # Test connection
#     with engine.connect() as connection:
#         print("Successfully connected to the database!")
# except Exception as e:
#     print(f"Failed to connect to the database. Error: {e}")
#     print("Please ensure your SQL Server is running and the SERVER_NAME in backend/database.py is correct.")
#     print("Common server names for local SQL Server Express: .\\SQLEXPRESS, (localdb)\\MSSQLLocalDB, YourComputerName")