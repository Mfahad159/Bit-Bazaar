from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas
from .database import SessionLocal # Removed unused 'engine' import for now

# If using SQLAlchemy to manage table creation (e.g., with Alembic or for initial setup):
# models.Base.metadata.create_all(bind=engine)
# Since tables are manually created, this is typically not run in production for existing schemas.

app = FastAPI(
    title="GameStore API",
    version="0.1.0",
    description="API for managing an online game store."
)

# Dependency: Get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================================================
#                                 API Endpoints for Games 
# ======================================================================================

@app.post("/games/", response_model=schemas.Game, status_code=status.HTTP_201_CREATED, tags=["Games"])
def create_game_endpoint(game: schemas.GameCreate, db: Session = Depends(get_db)):
    return crud.create_game(db=db, game=game)


@app.get("/games/", response_model=List[schemas.Game], tags=["Games"])
def read_games_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of games with optional pagination.
    """
    return crud.get_games(db, skip=skip, limit=limit)


@app.get("/games/{game_id}", response_model=schemas.Game, tags=["Games"])
def read_game_endpoint(game_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific game by its ID.
    """
    db_game = crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return db_game

@app.put("/games/{game_id}", response_model=schemas.Game, tags=["Games"])
def update_game_endpoint(game_id: int, game: schemas.GameUpdate, db: Session = Depends(get_db)):
    """
    Update an existing game's details.
    """
    db_game = crud.update_game(db=db, game_id=game_id, game_update=game)
    if db_game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return db_game

@app.delete("/games/{game_id}", response_model=schemas.Game, tags=["Games"])
def delete_game_endpoint(game_id: int, db: Session = Depends(get_db)):
    """
    Delete a game from the database.
    Returns the deleted game's data.
    """
    db_game = crud.delete_game(db=db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return db_game

@app.get("/", tags=["Root"], summary="Root path of the API")
async def root():
    """
    Welcome message for the API.
    """
    return {"message": "Welcome to the GameStore API!"}