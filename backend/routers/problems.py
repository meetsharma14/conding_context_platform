# ==================================
# IMPORTS
# ==================================

# FastAPI utilities
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

# Database session
from sqlalchemy.orm import Session

# Database connection dependency
from database import get_db

# Database models
from models import Problem, User

# Pydantic schemas
from schemas import (
    ProblemCreate,
    ProblemResponse
)

# Authentication and role checks
from auth import (
    get_current_user,
    get_admin_user
)


# ==================================
# ROUTER CONFIGURATION
# ==================================

router = APIRouter(

    # Base endpoint path
    prefix="/problems",

    # Group name in Swagger UI
    tags=["Problems"]
)


# ==================================
# CREATE PROBLEM
# ==================================

@router.post(
    "/",

    # Response schema
    response_model=ProblemResponse,

    # Return status code
    status_code=status.HTTP_201_CREATED
)
def create_problem(

    # Request body data
    problem: ProblemCreate,

    # Database dependency
    db: Session = Depends(get_db),

    # Enable this later if only admin can create
    # admin: User = Depends(get_admin_user)
):

    # Check whether problem already exists
    existing_problem = (

        db.query(Problem)

        .filter(
            Problem.title ==
            problem.title
        )

        .first()
    )

    # Duplicate problem validation
    if existing_problem:

        raise HTTPException(

            status_code=400,

            detail=
            "Problem already exists"
        )

    # Create new database object
    new_problem = Problem(

        title=problem.title,

        difficulty=problem.difficulty,

        description=problem.description,

        sample_input=
            problem.sample_input,

        sample_output=
            problem.sample_output
    )

    # Add object to database session
    db.add(
        new_problem
    )

    # Save changes
    db.commit()

    # Refresh object and get generated values
    db.refresh(
        new_problem
    )

    return new_problem


# ==================================
# GET ALL PROBLEMS
# ==================================

@router.get(
    "/",

    response_model=
    list[ProblemResponse]
)
def get_problems(

    # Optional difficulty filter
    difficulty: str | None = Query(
        default=None
    ),

    db: Session = Depends(
        get_db
    )
):

    # Select all problems
    query = db.query(
        Problem
    )

    # Apply difficulty filter
    if difficulty:

        query = query.filter(

            Problem.difficulty
            == difficulty
        )

    # Fetch data
    problems = query.all()

    return problems


# ==================================
# GET SINGLE PROBLEM
# ==================================

@router.get(

    "/{problem_id}",

    response_model=
    ProblemResponse
)
def get_problem(

    problem_id: int,

    db: Session = Depends(
        get_db
    )
):

    # Search by ID
    problem = (

        db.query(
            Problem
        )

        .filter(

            Problem.id
            == problem_id

        )

        .first()
    )

    # Problem not found
    if not problem:

        raise HTTPException(

            status_code=404,

            detail=
            "Problem not found"
        )

    return problem


# ==================================
# DELETE PROBLEM
# ==================================

@router.delete(
    "/{problem_id}"
)
def delete_problem(

    problem_id: int,

    db: Session = Depends(
        get_db
    ),

    # Only admin can delete
    admin: User = Depends(
        get_admin_user
    )
):

    # Find problem
    problem = (

        db.query(
            Problem
        )

        .filter(

            Problem.id
            == problem_id
        )

        .first()
    )

    # Problem does not exist
    if not problem:

        raise HTTPException(

            status_code=404,

            detail=
            "Problem not found"
        )

    # Remove from database
    db.delete(
        problem
    )

    db.commit()

    return {

        "message":
        "Problem deleted successfully"
    }


# ==================================
# USER ACCESS TEST
# ==================================

@router.get(
    "/me/test"
)
def test_user_access(

    # Verify JWT token
    current_user: User = Depends(
        get_current_user
    )
):

    return {

        "message":
        f"Welcome {current_user.username}",

        "role":
        current_user.role
    }