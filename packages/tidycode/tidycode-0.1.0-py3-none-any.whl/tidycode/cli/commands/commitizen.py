"""
Commitizen commands
"""

import subprocess
from pathlib import Path

import typer

from tidycode.core.bootstrap import setup_commitizen
from tidycode.utils import PYPROJECT_PATH

app = typer.Typer(help="Setup Commitizen")


def run_cz_command(args: list[str], cwd: Path | None = None) -> int:
    """Run a commitizen CLI command with given arguments."""
    command = ["cz"] + args
    try:
        result = subprocess.run(command, cwd=cwd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Commitizen command failed: {e}", err=True)
        return e.returncode


@app.command("setup")
def setup(pyproject: Path = None, dry_run: bool = False):
    """
    Add Commitizen config to pyproject.toml

    Args:
        pyproject (Path): Path to pyproject.toml file
        dry_run (bool): Show changes without writing to file or running commands
    """
    pyproject = pyproject or PYPROJECT_PATH

    try:
        success = setup_commitizen(pyproject, dry_run=dry_run)
    except Exception as e:
        print(f"Error in setup_commitizen: {e}")
        raise

    if not success:
        raise typer.Exit(code=1)


@app.command("init")
def cz_init(
    config: str = typer.Option(
        "cz_conventional_commits", help="Commitizen config name"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Automatic yes to prompts"),
    cwd: Path = Path("."),
):
    """Initialize Commitizen configuration."""
    args = ["init", "--name", config]
    if yes:
        args.append("--yes")
    code = run_cz_command(args, cwd)
    raise typer.Exit(code=code)


@app.command("changelog")
def cz_changelog(
    path: Path = Path("."),
    tag: str | None = typer.Option(None, help="Generate changelog for a specific tag"),
):
    """Generate changelog."""
    args = ["changelog"]
    if tag:
        args += ["--tag", tag]
    code = run_cz_command(args, path)
    raise typer.Exit(code=code)


@app.command("bump")
def cz_bump(
    no_verify: bool = typer.Option(False, "--no-verify", help="Skip pre-commit hooks"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Automatic yes to prompts"),
    path: Path = Path("."),
):
    """Bump version."""
    args = ["bump"]
    if no_verify:
        args.append("--no-verify")
    if yes:
        args.append("--yes")
    code = run_cz_command(args, path)
    raise typer.Exit(code=code)


@app.command("check")
def cz_check(
    commit_msg_file: Path = typer.Argument(..., help="Path to commit message file"),
):
    """Check commit message format."""
    args = ["check", "--commit-msg-file", str(commit_msg_file)]
    code = run_cz_command(args)
    raise typer.Exit(code=code)
