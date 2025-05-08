from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt 
from .security import create_access_token, verify_password 
from . import crud, models, schemas
from .database import SessionLocal 
from . import security 
from datetime import timedelta
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



# ======================================================================================
#                                 API Endpoints for Authentications 
# ======================================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@app.post("/users/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def signup_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user (signup).
    """
    # crud.create_user already handles email/username duplication checks and raises HTTPException
    db_user = crud.create_user(db=db, user=user)
    return db_user


@app.post("/auth/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Client should send 'username' (which we'll treat as email) and 'password' in form data.
    """
    print(f"--- AUTH: Login attempt for email: {form_data.username}") # DEBUG
    user = crud.get_user_by_email(db, email=form_data.username) # OAuth2 form uses 'username' field for the first credential

    if not user or not verify_password(form_data.password, user.password_hash):
        print(f"--- AUTH: Login FAILED for email: {form_data.username}") # DEBUG
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id, "role": user.role}, # 'sub' is standard for subject (often username/email)
        expires_delta=access_token_expires
    )
    print(f"--- AUTH: Login SUCCESS for email: {user.email}, token generated.") # DEBUG
    return {"access_token": access_token, "token_type": "bearer"}

# Placeholder for a protected route (we'll implement the actual protection later)
@app.get("/users/me", response_model=schemas.User, tags=["Users"])
async def read_users_me(db: Session = Depends(get_db), current_user_email: str = "test@example.com" ): # Replace default with Depends(get_current_active_user) later
    """
    Get current user details (requires authentication).
    THIS IS A PLACEHOLDER - actual authentication logic for current_user not yet implemented.
    """
    # This is a mock. We need to implement get_current_active_user dependency.
    # For now, just fetching a user based on a hardcoded or dummy email.
    # user = crud.get_user_by_email(db, email=current_user_email)
    # if user is None:
    #     raise HTTPException(status_code=404, detail="User not found (mock)")
    # return user
    print("WARNING: /users/me is a mock endpoint and does not enforce real authentication yet.")
    # For a quick test, let's try to get the first user or a specific one if exists
    user = db.query(models.User).first()
    if not user:
        return {"message": "No users in DB yet, /users/me is a mock."}
    return user # Returns the first user in the DB as a mock