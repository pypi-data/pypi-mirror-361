import keyword
import os
import re
import shutil
import typing as t
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
)

COMPONENT_FOLDERS: t.Dict[str, t.Callable[[dict], bool]] = {
    "bot": lambda config: True,
    "app": lambda config: config.get("use_webhook", False),
    "admin": lambda config: config.get("use_admin", False),
    "db": lambda config: config.get("use_db", False),
    "redis": lambda config: config.get("use_redis", False),
    "scheduler": lambda config: config.get("use_scheduler", False),
}

ENV_DEPENDENCIES = {
    "base": [
        ("TIMEZONE", "UTC"),
        ("DEFAULT_LOCALE", "en"),
        ("SUPPORTED_LOCALES", "en"),
    ],
    "bot": [
        ("BOT_TOKEN", "your_bot_token_here"),
        ("BOT_USERNAME", "your_bot_username_here"),
        ("BOT_DEV_ID", "123456789"),
        ("BOT_ADMINS", "123456789,987654321"),
    ],
    "webhook": [
        ("APP_URL", "https://your.domain.com"),
        ("APP_HOST", "0.0.0.0"),
        ("APP_PORT", "8000"),
    ],
    "db": {
        "PostgreSQL": [
            ("DB_URL", "postgresql+asyncpg://user:password@localhost:5432/dbname"),
        ],
        "MySQL": [
            ("DB_URL", "mysql+aiomysql://user:password@localhost:3306/dbname"),
        ],
        "SQLite": [
            ("DB_URL", "sqlite+aiosqlite:///./db.sqlite3"),
        ],
    },
    "redis": [
        ("REDIS_URL", "redis://localhost:6379/0"),
    ],
    "scheduler": [
        ("REDIS_URL", "redis://localhost:6379/0"),
    ],
    "admin": [
        ("ADMIN_TITLE", "Admin Panel"),
        ("ADMIN_BASE_URL", "/admin"),
    ],
}

DEPENDENCIES = {
    "base": [
        "aiogram>=3.21.0",
        "Jinja2>=3.1.0",
        "sulguk>=0.8.0",
        "environs>=14.2.0",
        "PyYAML>=6.0.2"
    ],
    "webhook": [
        "fastapi>=0.115.0",
        "uvicorn>=0.35.0",
        "starlette>=0.46.0",
    ],
    "db": {
        "base": ["SQLAlchemy>=2.0.0"],
        "PostgreSQL": ["asyncpg>=0.29.0"],
        "MySQL": ["aiomysql>=0.2.0"],
        "SQLite": ["aiosqlite>=0.21.0"],
    },
    "redis": ["redis>=6.2.0"],
    "scheduler": ["APScheduler>=3.11.0"],
    "admin": ["starlette-admin>=0.15.0"],
}


def is_valid_project_name(name: str) -> bool:
    return (
            re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name) is not None
            and not keyword.iskeyword(name)
    )


def get_template_dir() -> Path:
    return Path(__file__).parent / "template"


def render_jinja_template(src_path: Path, dst_path: Path, context: dict) -> None:
    env = Environment(
        loader=FileSystemLoader(str(src_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(src_path.name)
    content = template.render(**context)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(content)


def copy_or_render(src_dir: Path, dst_dir: Path, context: dict, allowed_folders: set) -> None:
    for root, dirs, files in os.walk(src_dir):
        rel_root = Path(root).relative_to(src_dir)
        if rel_root.parts and rel_root.parts[0] in COMPONENT_FOLDERS:
            if rel_root.parts[0] not in allowed_folders:
                continue
        target_root = dst_dir / rel_root
        target_root.mkdir(parents=True, exist_ok=True)
        j2_base_names = {f[:-3] for f in files if f.endswith(".j2")}
        for file in files:
            src_file = Path(root) / file
            if rel_root.parts == ("db",) and file == "config.py.j2":
                dst_file = target_root / "config.py"
                render_jinja_template(src_file, dst_file, context)
                continue
            if file.endswith(".j2"):
                out_name = file[:-3]
                dst_file = target_root / out_name
                render_jinja_template(src_file, dst_file, context)
            elif file not in j2_base_names:
                dst_file = target_root / file
                shutil.copy2(src_file, dst_file)


def generate_locales(dst_dir: Path) -> None:
    locales_dir = dst_dir.parent / "locales"
    locales_dir.mkdir(exist_ok=True)

    en_yml_path = locales_dir / "en.yml"
    if not en_yml_path.exists():
        content = (
            "echo: {{ message.text }}\n"
            "start: Hello {{ user.full_name }}, welcome to the bot!\n"
        )
        with open(en_yml_path, "w", encoding="utf-8") as f:
            f.write(content)


def generate_requirements(config: t.Dict[str, t.Any], dst_dir: Path) -> None:
    requirements: t.Set[str] = set(DEPENDENCIES["base"])

    if config.get("use_webhook"):
        requirements.update(DEPENDENCIES["webhook"])

    if config.get("use_db"):
        db_type = config.get("db_type")
        requirements.update(DEPENDENCIES["db"]["base"])
        if db_type in DEPENDENCIES["db"]:
            requirements.update(DEPENDENCIES["db"][db_type])

    if config.get("use_redis"):
        requirements.update(DEPENDENCIES["redis"])

    if config.get("use_scheduler"):
        requirements.update(DEPENDENCIES["scheduler"])

    if config.get("use_admin"):
        requirements.update(DEPENDENCIES["admin"])

    req_path = dst_dir.parent / "requirements.txt"
    with open(req_path, "w", encoding="utf-8") as f:
        for req in sorted(requirements, key=lambda s: s.lower()):
            f.write(f"{req}\n")


def generate_env(config: t.Dict[str, t.Any], dst_dir: Path) -> None:
    lines = []

    def add_env_block(block):
        for key, value in block:
            lines.append(f"{key}={value}")
        lines.append("")

    # Базовые переменные
    add_env_block(ENV_DEPENDENCIES["base"])
    # Переменные бота
    add_env_block(ENV_DEPENDENCIES["bot"])

    if config.get("use_webhook"):
        add_env_block(ENV_DEPENDENCIES["webhook"])

    if config.get("use_db"):
        db_type = config.get("db_type")
        db_block = ENV_DEPENDENCIES["db"].get(db_type)
        if db_block:
            add_env_block(db_block)

    if config.get("use_redis") or config.get("use_scheduler"):
        add_env_block(ENV_DEPENDENCIES["redis"])

    if config.get("use_admin"):
        add_env_block(ENV_DEPENDENCIES["admin"])

    env_path = dst_dir.parent / ".env"
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
