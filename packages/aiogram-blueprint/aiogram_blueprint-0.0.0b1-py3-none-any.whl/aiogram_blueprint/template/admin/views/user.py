from aiogram.enums import ChatMemberStatus
from babel.core import Locale
from starlette.requests import Request
from starlette_admin import *
from starlette_admin.contrib.sqla import ModelView

from ...constants import DEFAULT_LOCALE
from ...db.models import UserModel

STATE_CHOICES = (
    (ChatMemberStatus.KICKED.lower(), ChatMemberStatus.KICKED.title()),
    (ChatMemberStatus.MEMBER.lower(), ChatMemberStatus.MEMBER.title()),
)

LANGUAGE_CHOICES = tuple(
    (code, name.capitalize()) for code, name
    in Locale(DEFAULT_LOCALE).languages.items()
)


class UserView(ModelView):
    fields = [
        IntegerField(
            UserModel.id.name, "Telegram ID",
            read_only=True,
        ),
        EnumField(
            UserModel.state.name, "State",
            required=False,
            read_only=True,
            choices=STATE_CHOICES,
            maxlength=6,
        ),
        StringField(
            UserModel.username.name, "Username",
            required=False,
            maxlength=65,
        ),
        StringField(
            UserModel.full_name.name, "Full Name",
            required=True,
            maxlength=64,
        ),
        EnumField(
            UserModel.language_code.name, "Language",
            required=False,
            read_only=True,
            choices=LANGUAGE_CHOICES,
            maxlength=2,
        ),
        DateTimeField(
            UserModel.created_at.name, "Created at",
            read_only=True
        ),
        DateTimeField(
            UserModel.updated_at.name, "Updated at",
            read_only=True
        ),
    ]
    searchable_fields = [
        UserModel.id.key,
        UserModel.username.key,
        UserModel.full_name.key,
    ]
    sortable_field = [
        UserModel.id.key,
        UserModel.state.key,
        UserModel.created_at.key,
    ]

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False
