from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal # Important for handling prices correctly

# --- Game Schemas ---

# Base properties for a Game
class GameBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal
    genre: Optional[str] = None
    platform: Optional[str] = None
    release_date: Optional[date] = None
    stock_quantity: int = 0
    image_url: Optional[str] = None

    # Pydantic V2 Configuration
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) # Serialize Decimal to float in JSON responses
        }

# Schema for creating a new game (inherits from GameBase)
class GameCreate(GameBase):
    pass

# Schema for reading/returning game information (output)
class Game(GameBase): # Inherits from GameBase
    game_id: int
    created_at: datetime
    updated_at: datetime

    # Pydantic V2 Configuration (inherits and confirms from_attributes)
    class Config(GameBase.Config): # Inherit base config like json_encoders
        from_attributes = True # Ensures ORM mode compatibility

# Schema for updating a game (all fields optional)
class GameUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    genre: Optional[str] = None
    platform: Optional[str] = None
    release_date: Optional[date] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None

    # Pydantic V2 Configuration
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }

# --- User Schemas ---

# Base properties for a User
class UserBase(BaseModel):
    username: str
    email: EmailStr # Validates email format
    role: Optional[str] = 'customer' # Default role

# Properties to receive via API on user creation (signup)
class UserCreate(UserBase):
    password: str # Plain password, will be hashed in backend

# Properties to return to client (never include password_hash)
class User(UserBase):
    user_id: int
    created_at: datetime
    # is_active: bool # Example: if you add an is_active field to your User model

    # Pydantic V2 configuration
    class Config:
        from_attributes = True

# Properties for user login
class UserLogin(BaseModel):
    email: EmailStr # Or username, if you prefer login with username
    password: str

# --- Token Schemas (for JWT Authentication) ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None # Subject of the token (could be username)


# --- Order Schemas ---

# Schema for creating an order item (used within OrderCreate)
class OrderItemCreate(BaseModel):
    game_id: int
    quantity: int

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }



# Schema for reading an order item (includes the generated ID)
class OrderItem(OrderItemCreate):
    order_item_id: int
    price: Decimal  # Add price here

    class Config(OrderItemCreate.Config):
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }



# Schema for creating an order (input from the client)
class OrderCreate(BaseModel):
    user_id: int  # We'll get this from the token in the endpoint, but for simplicity of schema, we keep it.
    order_items: List[OrderItemCreate]

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }



# Schema for reading an order (output to the client)
class Order(OrderCreate):
    order_id: int
    order_date: datetime
    total_price: Decimal
    status: str  # Add status here
    order_items: List[OrderItem]

    class Config(OrderCreate.Config):  # Inherit the config and add to it.
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }
