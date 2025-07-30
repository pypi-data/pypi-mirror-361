import typing as t
from pathlib import Path
from zoneinfo import ZoneInfo

from environs import Env

ENV = Env()
ENV.read_env()

BASE_DIR = Path(__file__).resolve().parent
TIMEZONE = ZoneInfo(ENV.str("TIMEZONE", "UTC"))

LOCALES_DIR: Path = BASE_DIR.parent / "locales"
DEFAULT_LOCALE: str = ENV.str("DEFAULT_LOCALE", "en")
SUPPORTED_LOCALES: t.List[str] = ENV.list("SUPPORTED_LOCALES", default=[DEFAULT_LOCALE])
