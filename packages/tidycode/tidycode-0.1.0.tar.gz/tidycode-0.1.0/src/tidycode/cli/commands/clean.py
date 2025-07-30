"""
Clean commands
"""

import os
import shutil
from pathlib import Path

import typer

from tidycode.utils import EXCLUDE_DIRS, TARGETS

app = typer.Typer(help="Clean temporary and unwanted files")


def remove_path(path: Path):
    try:
        if path.is_dir():
            shutil.rmtree(path)
            # typer.echo(f"🗑️  Folder removed: {path}")
        elif path.is_file():
            path.unlink()
            # typer.echo(f"🗑️  File removed: {path}")
    except Exception as e:
        typer.echo(f"⚠️ Impossible to remove {path}: {e}")


@app.command("pycache")
def clean_pycache(path: Path = Path(".")):
    """
    Delete __pycache__ and .pyc files in the project.
    """
    root = path.resolve()
    count = 0
    for path in root.rglob("__pycache__"):
        remove_path(path)
        count += 1
    for path in root.rglob("*.pyc"):
        remove_path(path)
        count += 1
    typer.echo(f"✅ {count} files/folders cleaned (Python cache).")


@app.command("poetry-lock")
def clean_poetry_lock(path: Path = Path(".")):
    """
    Remove the poetry.lock file if it exists.
    """
    lock_file = path / "poetry.lock"
    if lock_file.exists():
        lock_file.unlink()
        typer.echo("✅ poetry.lock removed.")
    else:
        typer.echo("ℹ️ poetry.lock not found.")


@app.command("all")
def clean_all(path: Path = Path(".")):
    """
    Clean everything: python cache, poetry.lock, venv, etc.
    """
    typer.echo("🧹 Deep cleaning in progress...")

    clean_pycache()
    #clean_poetry_lock()

    extras = [
        ".venv",
        ".mypy_cache",
    ]

    root = path.resolve()
    deleted = 0
    for pattern in ["**/__pycache__", "**/*.pyo", "**/*.pyd"]:
        for p in root.glob(pattern):
            remove_path(p)
            deleted += 1
    for extra in extras:
        p = root / extra
        if p.exists():
            remove_path(p)
            deleted += 1

    typer.echo(f"✅ Deep cleaning completed ({deleted} items removed).")


@app.command("deep")
def clean_deep(path: Path = Path(".")):
    """
    Delete temporary and unwanted files by recursively traversing `path`.
    Exclude certain standard directories (git, venv...).
    """
    deleted = 0

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for name in files:
            full_path = Path(root) / name
            for pattern in TARGETS:
                if full_path.match(pattern):
                    remove_path(full_path)
                    deleted += 1

        for name in dirs:
            full_path = Path(root) / name
            if full_path.name in TARGETS or full_path.match("__pycache__"):
                remove_path(full_path)
                deleted += 1

    typer.echo(f"🧹 Deep cleaning completed. {deleted} files/folders removed.")
