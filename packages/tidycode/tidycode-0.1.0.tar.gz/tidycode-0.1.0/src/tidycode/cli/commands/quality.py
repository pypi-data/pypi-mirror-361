"""
Quality commands.
"""

from pathlib import Path

import typer

from tidycode.core.bootstrap.setup_tools import setup_tool_from_metadata
from tidycode.core.quality_tools import run_black, run_isort, run_mypy, run_ruff
from tidycode.utils import PYPROJECT_PATH

app = typer.Typer(help="Code quality commands")


@app.command("setup-black")
def setup_black(
    pyproject: Path = PYPROJECT_PATH,
    update_if_exists: bool = typer.Option(False),
    dry_run: bool = typer.Option(False),
):
    """Inject black config into pyproject.toml"""
    success = setup_tool_from_metadata(
        key="black",
        pyproject_path=pyproject,
        update_if_exists=update_if_exists,
        dry_run=dry_run,
    )
    if not success:
        raise typer.Exit(code=1)


@app.command("setup-ruff")
def setup_ruff(
    pyproject: Path = PYPROJECT_PATH,
    update_if_exists: bool = typer.Option(False),
    dry_run: bool = typer.Option(False),
):
    """Inject ruff config into pyproject.toml"""
    success = setup_tool_from_metadata(
        key="ruff",
        pyproject_path=pyproject,
        update_if_exists=update_if_exists,
        dry_run=dry_run,
    )
    if not success:
        raise typer.Exit(code=1)


@app.command("setup-isort")
def setup_isort(
    pyproject: Path = PYPROJECT_PATH,
    update_if_exists: bool = typer.Option(False),
    dry_run: bool = typer.Option(False),
):
    """Inject isort config into pyproject.toml"""
    success = setup_tool_from_metadata(
        key="isort",
        pyproject_path=pyproject,
        update_if_exists=update_if_exists,
        dry_run=dry_run,
    )
    if not success:
        raise typer.Exit(code=1)


@app.command("setup-mypy")
def setup_mypy(
    pyproject: Path = PYPROJECT_PATH,
    update_if_exists: bool = typer.Option(False),
    dry_run: bool = typer.Option(False),
):
    """Inject mypy config into pyproject.toml"""
    success = setup_tool_from_metadata(
        key="mypy",
        pyproject_path=pyproject,
        update_if_exists=update_if_exists,
        dry_run=dry_run,
    )
    if not success:
        raise typer.Exit(code=1)


@app.command("setup-all")
def setup_all(
    pyproject: Path = PYPROJECT_PATH,
    update_if_exists: bool = typer.Option(False),
    dry_run: bool = typer.Option(False),
):
    """Setup all tools"""
    setup_black(pyproject, update_if_exists, dry_run)
    setup_ruff(pyproject, update_if_exists, dry_run)
    setup_isort(pyproject, update_if_exists, dry_run)
    setup_mypy(pyproject, update_if_exists, dry_run)


@app.command("update-all")
def update_all(
    pyproject: Path = PYPROJECT_PATH,
):
    """Update all tools"""
    setup_all(pyproject, True, True)


@app.command()
def format(
    path: Path = typer.Argument(Path("."), help="Path to run black on."),
    check: bool = typer.Option(False, "--check", help="Only check without modifying."),
):
    """Run Black formatter."""
    success = run_black(path=path, check=check)
    if not success:
        raise typer.Exit(code=1)


@app.command("lint")
def lint(
    path: Path = typer.Argument(Path("."), help="Path to run ruff on."),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix lint issues."),
):
    """Run Ruff linter."""
    success = run_ruff(path=path, fix=fix)
    if not success:
        raise typer.Exit(code=1)


@app.command("imports")
def sort_imports(
    path: Path = typer.Argument(Path("."), help="Path to run isort on."),
    check: bool = typer.Option(False, "--check", help="Only check without modifying."),
):
    """Run isort on imports."""
    success = run_isort(path=path, check=check)
    if not success:
        raise typer.Exit(code=1)


@app.command("type-check")
def type_check(
    path: Path = typer.Argument(Path("."), help="Path to run mypy on."),
):
    """Run mypy static type checks."""
    success = run_mypy(path=path)
    if not success:
        raise typer.Exit(code=1)


@app.command("check-all")
def check_all(
    path: Path = typer.Argument(Path("."), help="Path to check all tools on."),
    fix: bool = typer.Option(False, "--fix", help="Fix with Ruff."),
    check: bool = typer.Option(False, "--check", help="Only check for Black/isort."),
):
    """Run all checks: ruff, black, isort, mypy"""
    failed = False

    if not run_ruff(path=path, fix=fix):
        failed = True
    if not run_black(path=path, check=check):
        failed = True
    if not run_isort(path=path, check=check):
        failed = True
    if not run_mypy(path=path):
        failed = True

    if failed:
        raise typer.Exit(code=1)
