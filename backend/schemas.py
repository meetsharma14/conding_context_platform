# ==================================
# PYDANTIC IMPORTS
# ==================================

# BaseModel → parent class for schemas
# EmailStr → validates email format
from pydantic import (
    BaseModel,
    EmailStr
)

# Used for date and time fields
from datetime import datetime

# Used for optional values
from typing import Optional


# ==================================
# USER SCHEMAS
# ==================================

# Input schema for user registration
class UserCreate(BaseModel):

    username: str

    # Automatically validates email
    email: EmailStr

    password: str


# Input schema for login
class UserLogin(BaseModel):

    username: str

    password: str
    requested_role: str


# Response schema returned after
# user creation/login
class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    role: str

    created_at: datetime

    class Config:

        # Allows conversion from
        # SQLAlchemy objects
        from_attributes = True


# ==================================
# TOKEN SCHEMAS
# ==================================

# JWT response structure
class Token(BaseModel):

    access_token: str

    token_type: str
    
    role: str          
    username: str       


# Stores token payload data
class TokenData(BaseModel):

    username: Optional[str] = None


# ==================================
# PROBLEM SCHEMAS
# ==================================

# Input schema for creating
# a coding problem
class ProblemCreate(BaseModel):

    title: str

    difficulty: str

    description: str

    sample_input: Optional[str] = None

    sample_output: Optional[str] = None


# Output schema returned
# when fetching problems
class ProblemResponse(BaseModel):

    id: int

    title: str

    difficulty: str

    description: str

    sample_input: Optional[str] = None

    sample_output: Optional[str] = None

    class Config:

        # Converts SQLAlchemy object
        # into JSON response
        from_attributes = True


# ==================================
# CONTEST SCHEMAS
# ==================================

# Input schema for contest creation
class ContestCreate(BaseModel):

    title: str

    description: str

    start_time: datetime

    end_time: datetime


# Contest response schema
class ContestResponse(BaseModel):

    id: int

    title: str

    description: str

    start_time: datetime

    end_time: datetime

    is_active: bool

    class Config:

        from_attributes = True


# ==================================
# SUBMISSION SCHEMAS
# ==================================

# Input schema for solution submission
class SubmissionCreate(BaseModel):

    problem_id: int

    code: str

    # Default language
    language: str = "python"


# Output schema for submissions
class SubmissionResponse(BaseModel):

    id: int

    user_id: int

    problem_id: int

    verdict: str

    score: int

    runtime_ms: int

    submitted_at: datetime

    class Config:

        from_attributes = True