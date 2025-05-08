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

    # When you define OrderItem model, you would uncomment and set this up:
    # order_items = relationship("OrderItem", back_populates="game")