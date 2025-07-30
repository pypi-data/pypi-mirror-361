from pathlib import Path

import click

from .survey import run_survey
from .utils import (
    COMPONENT_FOLDERS,
    copy_or_render,
    generate_env,
    generate_requirements,
    get_template_dir,
    is_valid_project_name, generate_locales,
)


@click.group()
def cli(): ...


@cli.command()
@click.argument("project_name", required=False)
def create(project_name: str) -> None:
    click.clear()
    click.secho("Welcome to the aiogram-blueprint project generator!\n", fg="blue", bold=True)

    config = run_survey()

    while True:
        while not project_name or not is_valid_project_name(project_name):
            if project_name:
                click.secho(
                    "Invalid project name! Use only letters, numbers, underscores, "
                    "do not start with a digit, and avoid Python keywords.",
                    fg="red", bold=True
                )
            project_name = click.prompt(
                click.style("Enter a valid project folder name", fg="cyan", bold=True),
                type=str,
            )

        dst_dir = Path.cwd() / project_name
        if dst_dir.exists():
            click.secho(
                f"Directory '{dst_dir}' already exists! Please choose another name.",
                fg="red", bold=True
            )
            project_name = None
            continue
        break

    allowed_folders = {name for name, cond in COMPONENT_FOLDERS.items() if cond(config)}
    copy_or_render(get_template_dir(), dst_dir, config, allowed_folders)

    click.secho(f"Project '{project_name}' created successfully at:", fg="green", bold=True, nl=False)
    click.secho(f" {dst_dir}", fg="cyan", bold=True)

    generate_requirements(config, dst_dir)
    generate_env(config, dst_dir)
    generate_locales(dst_dir)

    click.secho("\nNext steps:", fg="yellow", bold=True)
    click.secho("  1. Install dependencies: pip install -r requirements.txt", fg="blue")
    click.secho("  2. Fill in your .env file with real values", fg="blue")
    click.secho(f"  3. Run your bot: python -m {project_name}", fg="blue")
    click.secho("  4. Start building your bot!", fg="blue")
