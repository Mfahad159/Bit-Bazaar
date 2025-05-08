from sqlalchemy import Column, Integer, String, DECIMAL, DATE, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Game(Base):
    __tablename__ = "Games"

    game_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    description = Column(String, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    genre = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)
    release_date = Column(DATE, nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    image_url = Column(String(2048), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "Users" # Matches the table created with SQL

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True) # Indexed for faster lookups
    email = Column(String(100), unique=True, nullable=False, index=True) # Indexed for faster lookups
    password_hash = Column(String(255), nullable=False) # To store the hashed password
    role = Column(String(20), nullable=False, default='customer') # 'customer' or 'admin'
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # When you define OrderItem model, you would uncomment and set this up:
    # order_items = relationship("OrderItem", back_populates="game")