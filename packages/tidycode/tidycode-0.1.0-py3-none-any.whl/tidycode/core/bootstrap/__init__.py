"""
Bootstrap the project
"""

from .setup_commitizen import setup_commitizen
from .setup_dependabot import setup_dependabot
from .setup_hooks import setup_hooks, setup_hooks_minimal

__all__ = [
    "setup_hooks",
    "setup_hooks_minimal",
    "setup_commitizen",
    "setup_dependabot",
]
