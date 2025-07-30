from starlette_admin.contrib.sqla import Admin

from .user import UserView
from ...db.models import UserModel


def add_views(admin: Admin) -> None:
    admin.add_view(
        view=UserView(
            model=UserModel,
            name="User",
            label="Users",
        ),
    )
