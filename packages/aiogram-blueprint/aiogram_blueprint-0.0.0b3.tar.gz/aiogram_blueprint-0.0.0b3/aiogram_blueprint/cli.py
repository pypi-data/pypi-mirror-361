from pathlib import Path

import click

from .survey import run_survey
from .utils import (
    COMPONENT_FOLDERS,
    copy_or_render,
    get_template_dir, generate_requirements,
)


@click.group()
def cli(): ...


@cli.command()
@click.argument("project_name", required=False)
def create(project_name):
    print("Welcome to aiogram-blueprint project generator!\n")
    config = run_survey()
    if not project_name:
        project_name = click.prompt("Enter project folder name", type=str)
    dst_dir = Path.cwd() / project_name
    if dst_dir.exists():
        click.secho(f"Directory '{dst_dir}' already exists!", fg="red")
        return
    allowed_folders = {name for name, cond in COMPONENT_FOLDERS.items() if cond(config)}
    print("Generating project structure...")
    copy_or_render(get_template_dir(), dst_dir, config, allowed_folders)
    click.secho(f"Project '{project_name}' created successfully at {dst_dir}", fg="green")
    generate_requirements(config, dst_dir)


if __name__ == "__main__":
    cli()
