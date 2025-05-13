from backend import models, schemas
from . import models, schemas
from backend.security import get_password_hash
from sqlalchemy.orm import Session
from decimal import Decimal
from fastapi import HTTPException, status
from typing import List, Optional

#==============================================================================
# Function to get a game by its ID
#==============================================================================

def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.game_id == game_id).first()

#==============================================================================
# Function to get multiple games (with skip and limit for pagination)
#==============================================================================
def get_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Game).order_by(models.Game.game_id).offset(skip).limit(limit).all()

#==============================================================================
# Function to create a new game
#==============================================================================
def create_game(db: Session, game: schemas.GameCreate):

    print(f"--- CRUD: Attempting to create game. Title: {game.title}, Price: {game.price}") # DEBUG
    db_game = models.Game(
        title=game.title,
        description=game.description,
        price=game.price,
        genre=game.genre,
        platform=game.platform,
        release_date=game.release_date,
        stock_quantity=game.stock_quantity,
        image_url=game.image_url
    )
    db.add(db_game)
    try:
        db.commit()
        print(f"--- CRUD: Game '{game.title}' commit attempted successfully.") # DEBUG
        db.refresh(db_game) # Refresh to get DB-generated values like game_id, created_at
        print(f"--- CRUD: Game '{game.title}' refreshed. ID: {db_game.game_id}, Created At: {db_game.created_at}") # DEBUG
        return db_game
    except Exception as e:
        print(f"--- CRUD: ERROR during commit/refresh for game '{game.title}': {str(e)}") # DEBUG
        db.rollback() # Important: Rollback the session on error
        # Re-raise the exception so FastAPI returns a proper 500 error and logs it
        raise HTTPException(status_code=500, detail=f"Database error during game creation: {str(e)}")
    
#==============================================================================
# Function to update an existing game
#==============================================================================
def update_game(db: Session, game_id: int, game_update: schemas.GameUpdate):
    db_game = get_game(db, game_id=game_id)
    if not db_game:
        return None # Game not found

    update_data = game_update.model_dump(exclude_unset=True) # Pydantic V2
    # For Pydantic V1: update_data = game_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_game, key, value)

    # or the database trigger. If you want SQLAlchemy to manage it explicitly here:
    # db_game.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_game)
    return db_game
#==============================================================================
# Function to delete a game
#==============================================================================
def delete_game(db: Session, game_id: int):

    db_game = get_game(db, game_id=game_id)
    if not db_game:
        return None # Game not found

    db.delete(db_game)
    db.commit()
    return db_game # Return the deleted game data (or just True for success)



#==============================================================================
# --- User CRUD Functions ---
#==============================================================================
def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Get all users from the database.
    """
    return db.query(models.User).order_by(models.User.user_id).offset(skip).limit(limit).all()

    
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):

    print(f"--- CRUD: Hashing password for user: {user.email}") # DEBUG
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role if user.role else 'customer' # Ensure role is set
    )
    db.add(db_user)
    try:
        db.commit()
        print(f"--- CRUD: User '{user.email}' committed.") # DEBUG
        db.refresh(db_user)
        print(f"--- CRUD: User '{user.email}' refreshed. ID: {db_user.user_id}") # DEBUG
        return db_user
    except Exception as e: # Catch potential integrity errors (e.g., duplicate email/username)
        db.rollback()
        print(f"--- CRUD: ERROR creating user '{user.email}': {str(e)}") # DEBUG
        # Check for unique constraint violations (specific error message depends on DB)
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            # Determine if it's email or username by re-querying
            if get_user_by_email(db, email=user.email):
                raise HTTPException(status_code=409, detail=f"Email '{user.email}' already registered.")
            if get_user_by_username(db, username=user.username):
                raise HTTPException(status_code=409, detail=f"Username '{user.username}' already taken.")
        raise HTTPException(status_code=500, detail=f"Database error creating user: {str(e)}")
    

    #==============================================================================


def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    """
    Create a new order and its associated order items.
    """
    # Calculate the total price of the order.
    total_price = Decimal(0)
    for item in order.order_items:
        game = db.query(models.Game).get(item.game_id)
        if not game:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Game with id {item.game_id} not found")
        if item.quantity > game.stock_quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough stock for game {game.title} (id: {game.game_id}).  Requested {item.quantity}, available {game.stock_quantity}")
        total_price += game.price * item.quantity

    # Create the order.
    db_order = models.Order(
        user_id=order.user_id,
        total_price=total_price,
        status="pending",  # Set initial order status
    )
    db.add(db_order)
    db.flush()  # Need to flush to get the order_id

    # Create the order items.
    for item in order.order_items:
        game = db.query(models.Game).get(item.game_id) #get game again
        db_order_item = models.OrderItem(
            order_id=db_order.order_id,
            game_id=item.game_id,
            quantity=item.quantity,
            price=game.price,  # Current price
            price_at_purchase=game.price,  # Store the price at the time of order
        )
        db.add(db_order_item)
        game.stock_quantity -= item.quantity #reduce stock
        db.add(game)

    db.commit()
    db.refresh(db_order)  # Refresh the order to get the order_items
    return db_order
    


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    """
    Get an order by its ID.
    """
    return db.query(models.Order).filter(models.Order.order_id == order_id).first()


def get_orders_by_user(db: Session, user_id: int) -> List[models.Order]:
    """
    Get all orders for a specific user.
    """
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()


# Cart CRUD operations
def get_cart_item(db: Session, user_id: int, game_id: int):
    return db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.game_id == game_id
    ).first()

def get_cart_item_by_id(db: Session, cart_item_id: int):
    return db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()

def get_user_cart(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def create_cart_item(db: Session, cart_item: schemas.CartItemCreate, user_id: int):
    db_cart_item = models.CartItem(
        user_id=user_id,
        game_id=cart_item.game_id,
        quantity=cart_item.quantity
    )
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

def update_cart_item(db: Session, cart_item_id: int, quantity: int):
    db_cart_item = get_cart_item_by_id(db, cart_item_id)
    if db_cart_item:
        db_cart_item.quantity = quantity
        db.commit()
        db.refresh(db_cart_item)
    return db_cart_item

def delete_cart_item(db: Session, cart_item_id: int):
    db_cart_item = get_cart_item_by_id(db, cart_item_id)
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
    return db_cart_item

def create_payment(db: Session, payment: schemas.PaymentCreate, order=None) -> models.Payment:
    # If order is not provided, fetch it
    if order is None:
        order = db.query(models.Order).get(payment.order_id)
    # Generate transaction_id
    transaction_id = f"TXN-{order.order_id}-{int(order.order_date.timestamp())}" if order else None
    db_payment = models.Payment(
        order_id=payment.order_id,
        amount_paid=payment.amount_paid,
        payment_method=payment.payment_method,
        payment_status="Success",
        transaction_id=transaction_id,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment