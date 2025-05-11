from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from decimal import Decimal
from fastapi import File, UploadFile
from backend import crud, models, schemas, security
from .database import SessionLocal, Base, engine
import os
from datetime import timedelta
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GameStore API",
    version="0.1.0",
    description="API for managing an online game store."
)

# API routes should come before static file serving
api_app = FastAPI(title="GameStore API", version="0.1.0")
app.mount("/api", api_app)

# Image upload directory
UPLOAD_DIR = "backend/static/images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Serve static files for the frontend
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Serve frontend HTML files
@app.get("/")
async def read_root():
    return FileResponse("backend/static/index.html")

@app.get("/{filename}.html")
async def read_html(filename: str):
    return FileResponse(f"backend/static/{filename}.html")

# Catch-all route for other static files
@app.get("/{path:path}")
async def read_static(path: str):
    static_path = f"backend/static/{path}"
    if os.path.exists(static_path):
        return FileResponse(static_path)
    raise HTTPException(status_code=404, detail="File not found")

@api_app.post("/upload-image/", tags=["Images"])
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image to the server.
    """
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"image_url": f"/static/images/{file.filename}"}


# CORS middleware configuration
origins = [
    "http://localhost:8000",    # FastAPI server
    "http://127.0.0.1:8000",    # FastAPI server alternative
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency: Get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define where clients send username/password for a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

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
            detail="Insufficient privileges. Only admins can access this resource.",
        )
    return current_user


# ======================================================================================
#                                 API Endpoints for Games
# ======================================================================================

@api_app.post("/games/", response_model=schemas.Game, status_code=status.HTTP_201_CREATED, tags=["Games"])
def create_game_endpoint(game: schemas.GameCreate, db: Session = Depends(get_db)):
    return crud.create_game(db=db, game=game)


@api_app.get("/games/", response_model=List[schemas.Game], tags=["Games"])
def read_games_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of games with optional pagination.
    """
    return crud.get_games(db, skip=skip, limit=limit)


@api_app.get("/games/{game_id}", response_model=schemas.Game, tags=["Games"])
def read_game_endpoint(game_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific game by its ID.
    """
    db_game = crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return db_game

@api_app.put("/games/{game_id}", response_model=schemas.Game, tags=["Games"])
def update_game_endpoint(game_id: int, game: schemas.GameUpdate, db: Session = Depends(get_db)):
    """
    Update an existing game's details.
    """
    db_game = crud.update_game(db=db, game_id=game_id, game_update=game)
    if db_game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return db_game

@api_app.delete("/games/{game_id}", response_model=schemas.Game, tags=["Games"])
def delete_game_endpoint(game_id: int, db: Session = Depends(get_db)):
    """
    Delete a game from the database.
    Returns the deleted game's data.
    """
    db_game = crud.delete_game(db=db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return db_game

@api_app.post("/sample-games", tags=["Games"])
async def create_sample_games(db: Session = Depends(get_db)):
    sample_games = [
        schemas.GameCreate(
            title="The Witcher 3",
            description="An epic RPG with a rich, mature narrative",
            price=29.99,
            genre="RPG",
            image_url="/images/witcher3.jpg"
        ),
        schemas.GameCreate(
            title="Red Dead Redemption 2",
            description="A western-themed action-adventure game",
            price=49.99,
            genre="Action",
            image_url="/images/rdr2.jpg"
        ),
        schemas.GameCreate(
            title="FIFA 23",
            description="The latest in the FIFA series",
            price=39.99,
            genre="Sports",
            image_url="/images/fifa23.jpg"
        ),
        schemas.GameCreate(
            title="Minecraft",
            description="A sandbox game of creativity and survival",
            price=19.99,
            genre="Sandbox",
            image_url="/images/minecraft.jpg"
        ),
    ]
    
    created_games = []
    for game in sample_games:
        try:
            created_game = crud.create_game(db=db, game=game)
            created_games.append(created_game)
        except Exception as e:
            print(f"Error creating game {game.title}: {e}")
    
    return created_games

@api_app.get("/", tags=["Root"], summary="Root path of the API")
async def root():
    """
    Welcome message for the API.
    """
    return {"message": "Welcome to the GameStore API!"}

 # ======================================================================================
#                                 API Endpoints for Orders
# ======================================================================================
@api_app.post("/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Create a new order for the logged-in user.
    """
    # Override the user_id from the token, don't use the one from the request body
    order.user_id = current_user.user_id
    print(f"--- ORDER: Creating order for user_id: {order.user_id}") # Debug
    db_order = crud.create_order(db=db, order=order)
    return db_order

@api_app.get("/orders/{order_id}", response_model=schemas.Order, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve a specific order by its ID. Only the user who placed the order (or an admin) can access this.
    """
    db_order = crud.get_order(db, order_id=order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if db_order.user_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order.",
        )
    return db_order

@api_app.get("/orders/", response_model=List[schemas.Order], tags=["Orders"])
def get_user_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve all orders for the logged-in user.
    """
    db_orders = crud.get_orders_by_user(db, user_id=current_user.user_id)
    return db_orders


# ======================================================================================
#                                 API Endpoints for Authentication
# ======================================================================================

@api_app.post("/auth/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def signup_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user (signup).
    Ensure only one admin exists in the database.
    """
    if user.role == "admin":
        existing_admin = db.query(models.User).filter(models.User.role == "admin").first()
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An admin already exists. Only one admin is allowed."
            )

    # Default role to customer if not provided
    user.role = user.role if user.role else "customer"

    try:
        db_user = crud.create_user(db=db, user=user)
    except HTTPException as e:
        if e.status_code == 400 and "already exists" in e.detail:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email or username already exists")
        else:
            raise  # Re-raise other HTTPExceptions

    return db_user
    

@api_app.post("/auth/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login, get an access token for future requests.
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
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}



@api_app.get("/users/me", response_model=schemas.User, tags=["Users"])
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Get current authenticated user's details.
    """
    print(f"--- API: /users/me endpoint hit by authenticated user: {current_user.email}")
    return current_user


# ======================================================================================
#                                 API Endpoints for Cart
# ======================================================================================

@api_app.post("/cart/add", response_model=schemas.CartItem, status_code=status.HTTP_201_CREATED, tags=["Cart"])
def add_to_cart(cart_item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Add a game to the user's cart or update the quantity if it already exists.
    """
    existing_cart_item = crud.get_cart_item(db, user_id=current_user.user_id, game_id=cart_item.game_id)
    if existing_cart_item:
        # Update the quantity if the item already exists in the cart
        updated_cart_item = crud.update_cart_item(db, cart_item_id=existing_cart_item.id, quantity=existing_cart_item.quantity + cart_item.quantity)
        return updated_cart_item
    else:
        # Add a new item to the cart
        new_cart_item = crud.create_cart_item(db, cart_item=cart_item, user_id=current_user.user_id)
        return new_cart_item


@api_app.get("/cart/", response_model=List[schemas.CartItem], tags=["Cart"])
def get_cart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve all items in the user's cart.
    """
    return crud.get_user_cart(db, user_id=current_user.user_id)


@api_app.put("/cart/{cart_item_id}", response_model=schemas.CartItem, tags=["Cart"])
def update_cart_item(cart_item_id: int, cart_item_update: schemas.CartItemUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Update the quantity of a specific item in the user's cart.
    """
    db_cart_item = crud.get_cart_item_by_id(db, cart_item_id=cart_item_id)
    if not db_cart_item or db_cart_item.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    updated_cart_item = crud.update_cart_item(db, cart_item_id=cart_item_id, quantity=cart_item_update.quantity)
    return updated_cart_item


@api_app.delete("/cart/{cart_item_id}", response_model=schemas.CartItem, tags=["Cart"])
def delete_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Remove an item from the user's cart.
    """
    db_cart_item = crud.get_cart_item_by_id(db, cart_item_id=cart_item_id)
    if not db_cart_item or db_cart_item.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    deleted_cart_item = crud.delete_cart_item(db, cart_item_id=cart_item_id)
    return deleted_cart_item


@api_app.post("/cart/checkout", response_model=schemas.Order, status_code=status.HTTP_201_CREATED, tags=["Cart"])
def checkout_cart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Convert the user's cart into an order and clear the cart.
    """
    cart_items = crud.get_user_cart(db, user_id=current_user.user_id)
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    # Create an order from the cart items
    order_items = [schemas.OrderItemCreate(game_id=item.game_id, quantity=item.quantity) for item in cart_items]
    order = schemas.OrderCreate(user_id=current_user.user_id, order_items=order_items)
    db_order = crud.create_order(db=db, order=order)

    # Clear the cart
    for item in cart_items:
        crud.delete_cart_item(db, cart_item_id=item.id)

    return db_order