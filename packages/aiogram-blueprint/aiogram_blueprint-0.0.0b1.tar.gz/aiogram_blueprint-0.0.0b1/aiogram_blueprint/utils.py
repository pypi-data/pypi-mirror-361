import os
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

COMPONENT_FOLDERS = {
    "bot": lambda config: True,
    "app": lambda config: config.get("use_webhook", False),
    "admin": lambda config: config.get("use_admin", False),
    "db": lambda config: config.get("use_db", False),
    "redis": lambda config: config.get("use_redis", False),
    "scheduler": lambda config: config.get("use_scheduler", False),
}


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
        j2_basenames = {f[:-3] for f in files if f.endswith(".j2")}
        for file in files:
            src_file = Path(root) / file
            if (
                    rel_root.parts[:2] == ("bot", "middlewares")
                    and file in ("db.py", "db.py.j2")
                    and not context.get("use_db", False)
            ):
                continue
            if file.endswith(".j2"):
                out_name = file[:-3]
                dst_file = target_root / out_name
                render_jinja_template(src_file, dst_file, context)
            elif file not in j2_basenames:
                dst_file = target_root / file
                shutil.copy2(src_file, dst_file)
