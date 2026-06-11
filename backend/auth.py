# ==================================
# IMPORTS
# ==================================

# Used for token expiry time calculations
from datetime import datetime, timedelta

# JWT token encoding/decoding
from jose import JWTError, jwt

# Password hashing library
from passlib.context import CryptContext

# FastAPI authentication utilities
from fastapi import (
    Depends,
    HTTPException,
    status
)

# OAuth2 token extraction
from fastapi.security import (
    OAuth2PasswordBearer
)

# Database session type
from sqlalchemy.orm import Session


# Import database dependency
from database import get_db

# Import User model
from models import User


# ==================================
# JWT CONFIGURATION
# ==================================

# Secret key for signing JWT tokens
SECRET_KEY = "change_this_to_a_long_random_secret_key"

# JWT encryption algorithm
ALGORITHM = "HS256"

# Token validity time
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ==================================
# PASSWORD HASHING SETUP
# ==================================

# Using Argon2 hashing algorithm
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


# ==================================
# HASH PASSWORD
# Converts plain password into
# secure hashed password
# ==================================

def hash_password(password: str) -> str:

    # Minimum password validation
    if len(password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )

    # Generate hashed password
    return pwd_context.hash(
        password
    )


# ==================================
# VERIFY PASSWORD
# Compares entered password
# with stored hashed password
# ==================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ==================================
# USER AUTHENTICATION
# Checks username and password
# during login
# ==================================

def authenticate_user(
    username: str,
    password: str,
    db: Session
):

    # Search user in database
    user = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    # User not found
    if not user:
        return None

    # Password incorrect
    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user


# ==================================
# OAUTH2 TOKEN SETUP
# Reads Bearer token from requests
# ==================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# ==================================
# CREATE JWT TOKEN
# Generates access token
# ==================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
):

    # Copy user data
    to_encode = data.copy()

    # Calculate expiry time
    expire = datetime.utcnow() + (

        expires_delta

        if expires_delta

        else timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    # Add expiry inside payload
    to_encode.update(
        {"exp": expire}
    )

    # Encode token
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==================================
# GET CURRENT USER
# Reads JWT token and finds user
# ==================================

def get_current_user(

    token: str = Depends(
        oauth2_scheme
    ),

    db: Session = Depends(
        get_db
    )
):

    # Exception if token invalid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:

        # Decode JWT token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Extract username
        username = payload.get(
            "sub"
        )

        if username is None:
            raise credentials_exception

    except JWTError:

        raise credentials_exception

    # Find user in database
    user = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if user is None:

        raise credentials_exception

    return user


# ==================================
# ADMIN ACCESS CHECK
# Only admin users allowed
# ==================================

def get_admin_user(

    current_user: User = Depends(
        get_current_user
    )
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


# ==================================
# CONTEST CREATOR ACCESS
# Admin + Creator roles allowed
# ==================================

def get_contest_creator(

    current_user: User = Depends(
        get_current_user
    )
):

    if current_user.role not in [
        "admin",
        "creator"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Creator access required"
        )

    return current_user