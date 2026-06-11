# ==================================
# IMPORTS
# ==================================

# Used for date/time operations
from datetime import datetime

# FastAPI components
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

# Database session
from sqlalchemy.orm import Session

# Database dependency
from database import get_db

# Database models
from models import (
    Contest,
    ContestProblem,
    Problem,
    User
)

# Pydantic schemas
from schemas import (
    ContestCreate,
    ContestResponse
)

# Authentication dependencies
from auth import (
    get_admin_user,
    get_current_user
)


# ==================================
# ROUTER CONFIGURATION
# ==================================

router = APIRouter(

    # Base URL
    prefix="/contests",

    # Swagger documentation group
    tags=["Contests"]
)


# ==================================
# CREATE CONTEST
#
# Admin only
# ==================================

@router.post(
    "/",
    response_model=ContestResponse
)
def create_contest(

    # Request body data
    contest: ContestCreate,

    # Database connection
    db: Session = Depends(get_db),

    # Admin authentication
    admin: User = Depends(
        get_admin_user
    )
):

    # Create contest object
    new_contest = Contest(

        title=contest.title,

        description=contest.description,

        start_time=contest.start_time,

        end_time=contest.end_time,

        is_active=False
    )

    # Save in database
    db.add(new_contest)

    db.commit()

    db.refresh(new_contest)

    return new_contest


# ==================================
# GET ALL CONTESTS
# ==================================

@router.get(
    "/",
    response_model=list[ContestResponse]
)
def get_contests(
    db: Session = Depends(get_db)
):

    # Fetch all contests
    return db.query(
        Contest
    ).all()


# ==================================
# GET CONTEST BY ID
# ==================================

@router.get(
    "/{contest_id}"
)
def get_contest(

    contest_id: int,

    db: Session = Depends(
        get_db
    )
):

    # Search contest
    contest = (

        db.query(Contest)

        .filter(
            Contest.id == contest_id
        )

        .first()
    )

    # Contest not found
    if not contest:

        raise HTTPException(
            status_code=404,
            detail="Contest not found"
        )

    return contest


# ==================================
# ADD PROBLEM TO CONTEST
#
# Creates many-to-many relation
# ==================================

@router.post(
    "/{contest_id}/add-problem/{problem_id}"
)
def add_problem_to_contest(

    contest_id: int,

    problem_id: int,

    db: Session = Depends(get_db),

    admin: User = Depends(
        get_admin_user
    )
):

    # Verify contest exists
    contest = (

        db.query(Contest)

        .filter(
            Contest.id == contest_id
        )

        .first()
    )

    if not contest:

        raise HTTPException(
            status_code=404,
            detail="Contest not found"
        )

    # Verify problem exists
    problem = (

        db.query(Problem)

        .filter(
            Problem.id == problem_id
        )

        .first()
    )

    if not problem:

        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    # Create link table entry
    link = ContestProblem(

        contest_id=contest_id,

        problem_id=problem_id
    )

    db.add(link)

    db.commit()

    return {
        "message":
        "Problem added to contest"
    }


# ==================================
# START CONTEST
# ==================================

@router.put(
    "/{contest_id}/start"
)
def start_contest(

    contest_id: int,

    db: Session = Depends(
        get_db
    ),

    admin: User = Depends(
        get_admin_user
    )
):

    contest = (

        db.query(Contest)

        .filter(
            Contest.id == contest_id
        )

        .first()
    )

    if not contest:

        raise HTTPException(
            status_code=404,
            detail="Contest not found"
        )

    # Change status
    contest.is_active = True

    db.commit()

    return {
        "message":
        "Contest started"
    }


# ==================================
# END CONTEST
# ==================================

@router.put(
    "/{contest_id}/end"
)
def end_contest(

    contest_id: int,

    db: Session = Depends(
        get_db
    ),

    admin: User = Depends(
        get_admin_user
    )
):

    contest = (

        db.query(Contest)

        .filter(
            Contest.id == contest_id
        )

        .first()
    )

    if not contest:

        raise HTTPException(
            status_code=404,
            detail="Contest not found"
        )

    # Change status
    contest.is_active = False

    db.commit()

    return {
        "message":
        "Contest ended"
    }


# ==================================
# GET ACTIVE CONTESTS
# ==================================

@router.get(
    "/active/list"
)
def active_contests(

    db: Session = Depends(
        get_db
    )
):

    contests = (

        db.query(Contest)

        .filter(
            Contest.is_active == True
        )

        .all()
    )

    return contests