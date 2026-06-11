# ==================================
# IMPORTS
# ==================================

# FastAPI router and dependency injection
from fastapi import APIRouter, Depends

# Database session
from sqlalchemy.orm import Session

# SQL aggregation functions
from sqlalchemy import func

# Database connection dependency
from database import get_db

# Database models
from models import User, Submission


# ==================================
# ROUTER CONFIGURATION
# ==================================

router = APIRouter(

    # Base API route
    prefix="/leaderboard",

    # Swagger group name
    tags=["Leaderboard"]
)


# ==================================
# GLOBAL LEADERBOARD
# ==================================

@router.get("/")
def global_leaderboard(

    db: Session = Depends(get_db)
):

    # Query leaderboard statistics
    results = (

        db.query(

            # User information
            User.id,
            User.username,

            # Total score of all submissions
            func.coalesce(
                func.sum(
                    Submission.score
                ),
                0
            ).label(
                "total_score"
            ),

            # Count total submissions
            func.count(
                Submission.id
            ).label(
                "total_submissions"
            ),

            # Count accepted submissions
            func.sum(
                Submission.verdict == "Accepted"
            ).label(
                "accepted_count"
            )
        )

        # Include users even without submissions
        .outerjoin(

            Submission,

            User.id == Submission.user_id
        )

        # Group data by user
        .group_by(

            User.id,
            User.username
        )

        # Sort by highest score
        .order_by(

            func.coalesce(
                func.sum(
                    Submission.score
                ),
                0
            ).desc()
        )

        .all()
    )

    # Store leaderboard data
    leaderboard = []

    rank = 1

    # Convert query result into JSON response
    for row in results:

        leaderboard.append(

            {

                "rank": rank,

                "user_id": row.id,

                "username": row.username,

                "total_score":
                    row.total_score or 0,

                "total_submissions":
                    row.total_submissions or 0,

                "accepted":
                    row.accepted_count or 0
            }
        )

        rank += 1

    return leaderboard


# ==================================
# TOP 10 USERS
# ==================================

@router.get("/top10")
def top_10_users(

    db: Session = Depends(
        get_db
    )
):

    results = (

        db.query(

            User.username,

            # Sum total score
            func.coalesce(
                func.sum(
                    Submission.score
                ),
                0
            ).label(
                "score"
            )
        )

        # Join submission table
        .outerjoin(

            Submission,

            User.id == Submission.user_id
        )

        # Group by users
        .group_by(
            User.id
        )

        # Sort highest score first
        .order_by(

            func.coalesce(
                func.sum(
                    Submission.score
                ),
                0
            ).desc()
        )

        # Limit to top 10
        .limit(10)

        .all()
    )

    return results


# ==================================
# USER STATISTICS
# ==================================

@router.get(
    "/user/{user_id}"
)
def user_stats(

    user_id: int,

    db: Session = Depends(
        get_db
    )
):

    # Find user
    user = (

        db.query(User)

        .filter(
            User.id == user_id
        )

        .first()
    )

    # User not found
    if not user:

        return {
            "error":
            "User not found"
        }

    # Get user submissions
    submissions = (

        db.query(
            Submission
        )

        .filter(

            Submission.user_id
            == user_id

        )

        .all()
    )

    # Calculate total score
    total_score = sum(

        s.score
        for s in submissions
    )

    # Count accepted submissions
    accepted = len([

        s
        for s in submissions

        if s.verdict ==
        "Accepted"

    ])

    return {

        "username":
            user.username,

        "total_score":
            total_score,

        "total_submissions":
            len(submissions),

        "accepted":
            accepted
    }