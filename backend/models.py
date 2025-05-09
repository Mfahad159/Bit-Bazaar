from sqlalchemy import Column, Integer, String, DECIMAL, DATE, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "Orders"

    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    order_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_price = Column(Numeric(10, 2), nullable=False)  # Store total price with 2 decimal places
    status = Column(String(50), nullable=False, default="pending")  # e.g., pending, processing, shipped, delivered, cancelled

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")  # Cascade delete


class OrderItem(Base):
    __tablename__ = "OrderItems"

    order_item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("Orders.order_id"), nullable=False)
    game_id = Column(Integer, ForeignKey("Games.game_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Price of the game at the time of order
    price_at_purchase = Column(Numeric(10, 2), nullable=False)  # Price of the game at the time of order

    order = relationship("Order", back_populates="order_items")
    game = relationship("Game")  # No back_populates because Game doesn't have direct orders.



class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='customer')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user") # ADDED THIS LINE


class Game(Base):
    __tablename__ = "Games"
    game_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    genre = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)
    release_date = Column(DATE, nullable=True)
    stock_quantity = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
