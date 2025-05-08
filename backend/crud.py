from sqlalchemy.orm import Session
from . import models, schemas # Import our SQLAlchemy models and Pydantic schemas
from decimal import Decimal # Ensure Decimal is available for price updates
from fastapi import HTTPException
# Function to get a game by its ID
def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.game_id == game_id).first()

# Function to get multiple games (with skip and limit for pagination)
def get_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Game).offset(skip).limit(limit).all()

# Function to create a new game
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
# Function to update an existing game
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

# Function to delete a game
def delete_game(db: Session, game_id: int):
    db_game = get_game(db, game_id=game_id)
    if not db_game:
        return None # Game not found

    db.delete(db_game)
    db.commit()
    return db_game # Return the deleted game data (or just True for success)