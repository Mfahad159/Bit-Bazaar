from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from . import crud, models, schemas, security
from .database import SessionLocal
from datetime import timedelta

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

# Define where clients send username/password for a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

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
            price=game.price,  # Store the price at the time of order
        )
        db.add(db_order_item)
        game.stock_quantity -= item.quantity #reduce stock
        db.add(game)

    db.commit()
    db.refresh(db_order)  # Refresh the order to get the order_items
    return db_order
    
# Dependency to get the current user from a token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = security.decode_access_token(token, credentials_exception)
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    """
    Dependency to get the current user, and ensure they are an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges.  Only admins can access this resource.",
        )
    return current_user


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
#                                 API Endpoints for Orders
# ======================================================================================
@app.post("/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Create a new order for the logged-in user.
    """
    # Override the user_id from the token, don't use the one from the request body
    order.user_id = current_user.user_id
    print(f"--- ORDER: Creating order for user_id: {order.user_id}") # Debug
    db_order = crud.create_order(db=db, order=order)
    return db_order

@app.get("/orders/{order_id}", response_model=schemas.Order, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve a specific order by its ID.  Only the user who placed the order (or an admin, if you implement admin order viewing) can access this.
    """
    db_order = crud.get_order(db, order_id=order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if db_order.user_id != current_user.user_id and current_user.role != "admin": # added admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order.",
        )
    return db_order

@app.get("/users/orders/", response_model=List[schemas.Order], tags=["Orders"])
def get_user_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve all orders for the logged-in user.
    """
    db_orders = crud.get_orders_by_user(db, user_id=current_user.user_id)
    return db_orders


# ======================================================================================
#                                 API Endpoints for Authentications
# ======================================================================================


@app.post("/users/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def signup_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user (signup).
    The first user will be the admin.  Subsequent users will be customers.
    """
    # Check if any users exist.  If not, this user is the admin.
    if not crud.get_users(db):  # Use crud.get_users to check for any user
        user.role = "admin"
        print("--- AUTH: First user created as admin.")
    else:
        user.role = "customer"  # All subsequent users are customers.
        print("--- AUTH: New user created as customer.")

    try:
        db_user = crud.create_user(db=db, user=user)
    except HTTPException as e:
        if e.status_code == 400 and "already exists" in e.detail:
            #  returning the same error as before
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email or username already exists")
        else:
            raise  # Re-raise other HTTPExceptions

    return db_user
    

@app.post("/auth/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Client should send 'username' (which we'll treat as email) and 'password' in form data.
    """
    print(f"--- AUTH: Login attempt for email: {form_data.username}")
    user = crud.get_user_by_email(db, email=form_data.username)

    if not user or not security.verify_password(form_data.password, user.password_hash):
        print(f"--- AUTH: Login FAILED for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email, "user_id": user.user_id, "role": user.role},
        expires_delta=access_token_expires
    )
    print(f"--- AUTH: Login SUCCESS for email: {user.email}, token generated.")
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/users/me", response_model=schemas.User, tags=["Users"])
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Get current authenticated user's details.
    """
    print(f"--- API: /users/me endpoint hit by authenticated user: {current_user.email}")
    return current_user
