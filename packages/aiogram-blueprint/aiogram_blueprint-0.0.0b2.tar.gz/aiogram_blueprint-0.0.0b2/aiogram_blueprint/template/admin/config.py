from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..constants import BASE_DIR, ENV

TEMPLATES_DIR = BASE_DIR / "admin" / "templates"


@dataclass(frozen=True)
class AdminConfig:
    TITLE: str
    BASE_URL: str
    TEMPLATES_DIR: Path

    @classmethod
    def load(cls) -> AdminConfig:
        return cls(
            TITLE=ENV.str("ADMIN_TITLE", "Admin Panel"),
            BASE_URL=ENV.str("ADMIN_BASE_URL", "/admin"),
            TEMPLATES_DIR=ENV.path("TEMPLATES_DIR", default=TEMPLATES_DIR)
        )


admin_config = AdminConfig.load()
