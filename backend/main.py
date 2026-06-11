# ==================================
# FASTAPI IMPORTS
# ==================================

# Main FastAPI framework
from fastapi import FastAPI

# Middleware for frontend-backend communication
from fastapi.middleware.cors import (
    CORSMiddleware
)


# ==================================
# DATABASE IMPORTS
# ==================================

# Database engine and Base class
from database import engine, Base


# ==================================
# IMPORT MODELS
#
# Import models so SQLAlchemy
# registers all tables
# ==================================

from models import (
    User,
    Problem,
    Contest,
    ContestProblem,
    Submission
)


# ==================================
# IMPORT ROUTERS
#
# Each router handles a module
# of the application
# ==================================

from routers.users import (
    router as users_router
)

from routers.problems import (
    router as problems_router
)

from routers.contests import (
    router as contests_router
)

from routers.submissions import (
    router as submissions_router
)

from routers.leaderboard import (
    router as leaderboard_router
)
from admin import setup_admin

# ==================================
# CREATE DATABASE TABLES
#
# Creates tables automatically
# if they do not exist
# ==================================

Base.metadata.create_all(
    bind=engine
)


# ==================================
# CREATE FASTAPI APPLICATION
# ==================================

app = FastAPI(

    title="Coding Contest Platform",

    description=
    "Real-Time Coding Contest Platform API",

    version="1.0.0"
)
setup_admin(app)

# ==================================
# CORS CONFIGURATION
#
# Allows frontend (Streamlit)
# to communicate with backend
#
# Without CORS browser blocks
# requests for security reasons
# ==================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        # Streamlit local server
        "http://localhost:8501",

        "http://127.0.0.1:8501"
    ],

    # Allow cookies/tokens
    allow_credentials=True,

    # Allow all HTTP methods
    allow_methods=["*"],

    # Allow all request headers
    allow_headers=["*"]
)


# ==================================
# REGISTER ROUTERS
#
# Connect application routes
# ==================================

app.include_router(
    users_router
)

app.include_router(
    problems_router
)

app.include_router(
    contests_router
)

app.include_router(
    submissions_router
)

app.include_router(
    leaderboard_router
)


# ==================================
# ROOT ROUTE
#
# Default API route
# ==================================

@app.get("/")
def home():

    return {

        "message":
        "Coding Contest Platform API Running "
    }


# ==================================
# HEALTH CHECK ROUTE
#
# Used to verify API status
# ==================================

@app.get("/health")
def health():

    return {

        "status": "healthy"
    }


# ==================================
# API INFORMATION ROUTE
#
# Returns application details
# ==================================

@app.get("/info")
def info():

    return {

        "project":
        "Coding Contest Platform",

        "version":
        "1.0.0",

        "features": [

            "Authentication",

            "Problems",

            "Contests",

            "Submissions",

            "Leaderboard"
        ]
    }


# ==================================
# APPLICATION STARTUP EVENT
#
# Runs automatically when API starts
# ==================================

@app.on_event("startup")
def startup():

    print(
        "Coding Contest Platform started successfully"
    )