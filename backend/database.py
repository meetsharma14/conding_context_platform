# ==================================
# SQLAlchemy Imports
# create_engine -> Creates DB connection
# sessionmaker -> Creates DB sessions
# declarative_base -> Base class for models
# ==================================

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)


# ==================================
# DATABASE CONFIGURATION
# SQLite database file
# Can later be changed to MySQL/PostgreSQL
# ==================================

DATABASE_URL = "sqlite:///./coding_contest.db"


# ==================================
# CREATE DATABASE ENGINE
# check_same_thread=False:
# Allows multiple requests to access
# SQLite in FastAPI
# ==================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# ==================================
# CREATE DATABASE SESSION FACTORY
#
# autocommit=False:
# Changes save only after commit()
#
# autoflush=False:
# Avoids automatic updates before commit
#
# bind=engine:
# Connect session to database engine
# ==================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==================================
# BASE CLASS FOR MODELS
#
# Every SQLAlchemy model inherits
# from this Base class
#
# Example:
#
# class User(Base):
#     __tablename__="users"
# ==================================

Base = declarative_base()


# ==================================
# DATABASE DEPENDENCY
#
# Creates DB session for request
# Opens session at start
# Closes session automatically
#
# Used in FastAPI:
#
# db: Session = Depends(get_db)
# ==================================

def get_db():

    db = SessionLocal()

    try:

        # Give database session
        yield db

    finally:

        # Close session after use
        db.close()