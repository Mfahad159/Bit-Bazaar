from . import models, schemas 
from .security import get_password_hash #
from sqlalchemy.orm import Session
from . import models, schemas # Import our SQLAlchemy models and Pydantic schemas
from decimal import Decimal 
from fastapi import HTTPException

#==============================================================================
# Function to get a game by its ID
#==============================================================================

def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.game_id == game_id).first()

#==============================================================================
# Function to get multiple games (with skip and limit for pagination)
#==============================================================================
def get_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Game).offset(skip).limit(limit).all()

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