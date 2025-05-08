from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal # Important for handling prices correctly

# Schema for creating a new game (input)
# What the client needs to send us
class GameBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal           # Pydantic will validate this is a valid decimal
    genre: Optional[str] = None
    platform: Optional[str] = None
    release_date: Optional[date] = None
    stock_quantity: int = 0
    image_url: Optional[str] = None


    class Config:
        # orm_mode = True # Will enable this for the response model
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) # Serialize Decimal to float in JSON responses
        }


class GameCreate(GameBase):
    pass # Inherits all fields from GameBase, no new fields for creation
# Schema for reading/returning game information (output)
# What we send back to the client
class Game(GameBase): # Inherits from GameBase
    game_id: int
    created_at: datetime
    updated_at: datetime

    # This tells Pydantic to read data from ORM models (like our SQLAlchemy Game model)
    # Pydantic V1:
    # class Config:
    #     orm_mode = True
    # Pydantic V2:
    class Config(GameBase.Config): # Inherit base config
        from_attributes = True # Replaces orm_mode in Pydantic V2


# Optional: Schema for updating a game (all fields optional)
class GameUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    genre: Optional[str] = None
    platform: Optional[str] = None
    release_date: Optional[date] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None

    class Config:
        # For Pydantic V2:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }