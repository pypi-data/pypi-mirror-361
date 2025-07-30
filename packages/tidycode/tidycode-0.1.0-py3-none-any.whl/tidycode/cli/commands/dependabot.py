"""
Dependabot commands
"""

from pathlib import Path

import typer

from tidycode.core.bootstrap import setup_dependabot
from tidycode.utils import DEPENDABOT_PATH

app = typer.Typer(help="Setup dependabot.yml")


@app.command("setup")
def setup(path: Path = DEPENDABOT_PATH):
    """Create dependabot.yml config"""
    setup_dependabot(path)
