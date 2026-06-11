from starlette_admin.contrib.sqla import Admin, ModelView

from database import engine
from models import (
    User,
    Problem,
    Contest,
    ContestProblem,
    Submission
)

def setup_admin(app):

    admin = Admin(
        engine=engine,
        title="Coding Contest Admin"
    )

    admin.add_view(ModelView(User))
    admin.add_view(ModelView(Problem))
    admin.add_view(ModelView(Contest))
    admin.add_view(ModelView(ContestProblem))
    admin.add_view(ModelView(Submission))

    admin.mount_to(app)