# ==================================
# IMPORTS
# ==================================

# FastAPI utilities
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

# Database session
from sqlalchemy.orm import Session

# Database connection dependency
from database import get_db

# Database model
from models import User

# Pydantic schemas
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token
)

# Authentication utilities
from auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user
)


# ==================================
# ROUTER CONFIGURATION
# ==================================

router = APIRouter(

    # Base endpoint URL
    prefix="/users",

    # Group name in Swagger UI
    tags=["Users"]
)


# ==================================
# USER REGISTRATION
# ==================================

@router.post(

    "/register",

    # Expected response schema
    response_model=UserResponse
)
def register(

    # Request body
    user: UserCreate,

    # Database dependency
    db: Session = Depends(get_db)
):

    # Check if username exists
    existing_username = (

        db.query(User)

        .filter(
            User.username
            == user.username
        )

        .first()
    )

    if existing_username:

        raise HTTPException(

            status_code=400,

            detail=
            "Username already exists"
        )

    # Check if email exists
    existing_email = (

        db.query(User)

        .filter(
            User.email
            == user.email
        )

        .first()
    )

    if existing_email:

        raise HTTPException(

            status_code=400,

            detail=
            "Email already exists"
        )

    # Create new user object
    new_user = User(

        username=
            user.username,

        email=
            user.email,

        # Store hashed password
        password_hash=
            hash_password(
                user.password
            ),

        role=
            "participant"
    )

    # Add to database session
    db.add(
        new_user
    )

    # Save data
    db.commit()

    # Refresh object and get generated fields
    db.refresh(
        new_user
    )

    return new_user


# ==================================
# USER LOGIN
# ==================================

# ==================================
# USER LOGIN
# ==================================

@router.post(
    "/login",
    response_model=Token
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    # 1. Authenticate user (Check username and password)
    user = authenticate_user(
        credentials.username,
        credentials.password,
        db
    )

    # Invalid credentials
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # 2. ROLE AUTHORIZATION LOGIC
    # Convert requested role to lowercase for consistency
    req_role = credentials.requested_role.lower()

    # If they want to login as Admin, but are only a Participant in the DB
    if req_role == "admin" and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to log in as an Admin."
        )
    
    # Note: If an 'admin' user wants to login as a 'participant', we allow it.
    # This is useful for admins who want to see the student view.

    # 3. Generate JWT token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": req_role  # Store the active role in the token
        }
    )

    # 4. Return response
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": req_role,        # The role they are logging in as
        "username": user.username
    }
# ==================================
# CURRENT USER PROFILE
# ==================================

@router.get(

    "/me",

    response_model=
    UserResponse
)
# ==================================
# GET ALL USERS
# ==================================

@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_all_users(

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    users = (

        db.query(User)

        .all()
    )

    return users
def get_profile(

    # Verify logged-in user
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user