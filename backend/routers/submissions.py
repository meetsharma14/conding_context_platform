# ==================================
# IMPORTS
# ==================================

# FastAPI tools
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

# SQLAlchemy database session
from sqlalchemy.orm import Session

# Database dependency
from database import get_db

# Database models
from models import (
    Submission,
    Problem,
    User
)

# Pydantic schemas
from schemas import (
    SubmissionCreate,
    SubmissionResponse
)

# Authentication dependency
from auth import (
    get_current_user
)

# Online judge logic
from judge import run_python_code


# ==================================
# ROUTER CONFIGURATION
# ==================================

router = APIRouter(

    # Base endpoint path
    prefix="/submissions",

    # Swagger API group
    tags=["Submissions"]
)


# ==================================
# SAMPLE TEST CASES
# ==================================
# Temporary hardcoded test cases
# Later these can be stored in database

SAMPLE_TEST_CASES = {

    # Problem ID = 1
    1: [

        {
            "input": [2,3],
            "output": 5
        },

        {
            "input": [10,20],
            "output": 30
        }
    ],

    # Problem ID = 2
    2: [

        {
            "input":[5,5],
            "output":10
        }
    ]
}


# ==================================
# SUBMIT SOLUTION
# ==================================

@router.post(
    "/",
    response_model=SubmissionResponse
)
def submit_solution(

    # Submission request body
    submission: SubmissionCreate,

    # Database dependency
    db: Session = Depends(get_db),

    # Logged-in user
    current_user: User = Depends(
        get_current_user
    )
):

    # Check whether problem exists
    problem = (

        db.query(
            Problem
        )

        .filter(

            Problem.id ==
            submission.problem_id

        )

        .first()
    )

    if not problem:

        raise HTTPException(

            status_code=404,

            detail=
            "Problem not found"
        )

    # Load test cases
    test_cases = SAMPLE_TEST_CASES.get(

        submission.problem_id
    )

    # If no test cases exist
    if not test_cases:

        raise HTTPException(

            status_code=404,

            detail=
            "No test cases found"
        )

    # Run code in judge system
    judge_result = run_python_code(

        submission.code,

        test_cases
    )

    # Create submission object
    new_submission = Submission(

        user_id=current_user.id,

        problem_id=
            submission.problem_id,

        code=
            submission.code,

        language=
            submission.language,

        verdict=
            judge_result["verdict"],

        score=
            judge_result["score"],

        runtime_ms=
            judge_result["runtime_ms"]
    )

    # Save submission
    db.add(
        new_submission
    )

    db.commit()

    db.refresh(
        new_submission
    )

    return new_submission


# ==================================
# GET CURRENT USER SUBMISSIONS
# ==================================

@router.get(
    "/my",
    response_model=
    list[SubmissionResponse]
)
def my_submissions(

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    submissions = (

        db.query(
            Submission
        )

        .filter(

            Submission.user_id
            == current_user.id

        )

        .order_by(

            Submission.submitted_at
            .desc()

        )

        .all()
    )

    return submissions


# ==================================
# GET ALL SUBMISSIONS
# ==================================

@router.get(
    "/",
    response_model=
    list[SubmissionResponse]
)
def get_all_submissions(

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    submissions = (

        db.query(
            Submission
        )

        .order_by(
            Submission.submitted_at
            .desc()
        )

        .all()
    )

    return submissions


# ==================================
# GET SUBMISSION BY ID
# ==================================

@router.get(
    "/{submission_id}",
    response_model=SubmissionResponse
)
def get_submission(

    submission_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    submission = (

        db.query(
            Submission
        )

        .filter(

            Submission.id ==
            submission_id
        )

        .first()
    )

    if not submission:

        raise HTTPException(

            status_code=404,

            detail=
            "Submission not found"
        )

    return submission