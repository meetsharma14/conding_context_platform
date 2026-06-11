# ==================================
# SQLAlchemy IMPORTS
# ==================================

# Used to create table columns
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
)

# Used for table relationships
from sqlalchemy.orm import relationship

# Used for timestamps
from datetime import datetime


# Import Base class from database.py
from database import Base


# ==================================
# USERS TABLE
# ==================================

class User(Base):

    # Database table name
    __tablename__ = "users"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Unique username
    username = Column(
        String(50),
        unique=True,
        nullable=False
    )

    # Unique email
    email = Column(
        String(120),
        unique=True,
        nullable=False
    )

    # Store hashed password only
    password_hash = Column(
        String(255),
        nullable=False
    )

    # User role
    # participant/admin/creator
    role = Column(
        String(20),
        default="participant"
    )

    # User creation timestamp
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # One user → many submissions
    submissions = relationship(
        "Submission",
        back_populates="user",
        cascade="all, delete"
    )


# ==================================
# PROBLEMS TABLE
# ==================================

class Problem(Base):

    __tablename__ = "problems"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Problem title
    title = Column(
        String(255),
        nullable=False
    )

    # Difficulty level

    difficulty = Column(
        String(20),
        nullable=False
    )

    # Full problem statement
    description = Column(
        Text,
        nullable=False
    )

    # Example input/output
    sample_input = Column(Text)

    sample_output = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # One problem → many submissions
    submissions = relationship(
        "Submission",
        back_populates="problem"
    )

    # Problem linked to contests
    contest_links = relationship(
        "ContestProblem",
        back_populates="problem",
        cascade="all, delete"
    )


# ==================================
# CONTEST TABLE
# ==================================

class Contest(Base):

    __tablename__ = "contests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text
    )

    # Contest start/end time
    start_time = Column(
        DateTime
    )

    end_time = Column(
        DateTime
    )

    # Contest active status
    is_active = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # One contest → many problems
    problems = relationship(
        "ContestProblem",
        back_populates="contest",
        cascade="all, delete"
    )


# ==================================
# CONTEST ↔ PROBLEM LINK TABLE
#
# Many-to-many relationship
#
# One contest → many problems
# One problem → many contests
# ==================================

class ContestProblem(Base):

    __tablename__ = "contest_problems"

    id = Column(
        Integer,
        primary_key=True
    )

    contest_id = Column(
        Integer,
        ForeignKey(
            "contests.id"
        )
    )

    problem_id = Column(
        Integer,
        ForeignKey(
            "problems.id"
        )
    )

    contest = relationship(
        "Contest",
        back_populates="problems"
    )

    problem = relationship(
        "Problem",
        back_populates="contest_links"
    )


# ==================================
# SUBMISSIONS TABLE
# ==================================

class Submission(Base):

    __tablename__ = "submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Foreign key → users table
    user_id = Column(
        Integer,
        ForeignKey(
            "users.id"
        )
    )

    # Foreign key → problems table
    problem_id = Column(
        Integer,
        ForeignKey(
            "problems.id"
        )
    )

    # Submitted code
    code = Column(
        Text,
        nullable=False
    )

    # Programming language
    language = Column(
        String(20),
        default="python"
    )

    # Result status
    verdict = Column(
        String(50),
        default="Pending"
    )

    # Submission score
    score = Column(
        Integer,
        default=0
    )

    # Runtime in milliseconds
    runtime_ms = Column(
        Integer,
        default=0
    )

    # Submission timestamp
    submitted_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Many submissions → one user
    user = relationship(
        "User",
        back_populates="submissions"
    )

    # Many submissions → one problem
    problem = relationship(
        "Problem",
        back_populates="submissions"
    )