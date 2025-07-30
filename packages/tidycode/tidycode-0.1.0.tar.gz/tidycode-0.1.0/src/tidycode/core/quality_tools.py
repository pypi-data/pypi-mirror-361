"""
Quality tools.
"""

import subprocess
from pathlib import Path

from tidycode.utils import run_command


def run_black(path: Path = Path("."), check: bool = False) -> bool:
    """
    Run black formatter.

    Args:
        path (Path): Directory or file to format (default: current directory).
        check (bool): If True, only check for formatting without modifying.

    Returns:
        bool: True if success, False otherwise.
    """
    command = ["black", str(path)]
    if check:
        command.append("--check")

    try:
        run_command(command, check=True)
        print("✅ Formatting succeeded.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Formatting failed.")
        return False


def run_ruff(path: Path = Path("."), fix: bool = False) -> bool:
    """
    Run ruff linter.

    Args:
        path (Path): Directory or file to lint (default: current directory).
        fix (bool): If True, fix linting errors.

    Returns:
        bool: True if success, False otherwise.
    """
    command = ["ruff", "check", str(path)]
    if fix:
        command.append("--fix")
    try:
        run_command(command, check=True)
        print("✅ Ruff passed.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ruff failed.")
        return False


def run_isort(path: Path = Path("."), check: bool = False) -> bool:
    """
    Run isort formatter.

    Args:
        path (Path): Directory or file to format (default: current directory).
        check (bool): If True, only check for formatting without modifying.

    Returns:
        bool: True if success, False otherwise.
    """
    command = ["isort", str(path)]
    if check:
        command.append("--check-only")
    try:
        run_command(command, check=True)
        print("✅ isort passed.")
        return True
    except subprocess.CalledProcessError:
        print("❌ isort failed.")
        return False


def run_mypy(path: Path = Path(".")) -> bool:
    """
    Run mypy type checker.

    Args:
        path (Path): Directory or file to check (default: current directory).

    Returns:
        bool: True if success, False otherwise.
    """
    command = ["mypy", str(path)]
    try:
        run_command(command, check=True)
        print("✅ mypy passed.")
        return True
    except subprocess.CalledProcessError:
        print("❌ mypy failed.")
        return False
