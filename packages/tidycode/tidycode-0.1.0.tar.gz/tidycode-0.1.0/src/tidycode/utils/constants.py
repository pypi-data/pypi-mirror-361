"""
Constants for the project
"""

from pathlib import Path

CONFIG_FILE_PATH = Path(".pre-commit-config.yaml")
PYPROJECT_PATH = Path("pyproject.toml")
DEPENDABOT_PATH = Path(".github/dependabot.yml")

EXCLUDE_DIRS = {".git", ".venv", "node_modules", "dist", "__pypackages__"}
TARGETS = [
    "__pycache__",
    "*.log",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "*.egg-info",
    "*.pyc",
    "*.pyo",
    ".ruff_cache",
    ".pytest_cache",
]
