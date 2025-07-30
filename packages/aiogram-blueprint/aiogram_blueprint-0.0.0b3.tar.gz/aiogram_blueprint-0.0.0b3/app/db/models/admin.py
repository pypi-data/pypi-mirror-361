from __future__ import annotations

from sqlalchemy import (
    BigInteger,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from .base import BaseModel
from .mixins import ModelCreatedAtMixin


class AdminModel(BaseModel, ModelCreatedAtMixin):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False,
    )
