"""
Main CLI
"""

import subprocess
import typer

from .commands import clean, commitizen, configs, dependabot, hooks, quality

app = typer.Typer(help="Tidycode is a tool to help you keep your code clean and tidy.")

app.add_typer(hooks.app, name="hooks")
app.add_typer(commitizen.app, name="commitizen")
app.add_typer(dependabot.app, name="dependabot")
app.add_typer(configs.app, name="configs")
app.add_typer(clean.app, name="clean")
app.add_typer(quality.app, name="quality")


@app.command("init")
def init():
    """Initialize a new project"""
    hooks.setup_hooks_minimal()
    commitizen.setup()
    dependabot.setup()
    quality.setup_all(update_if_exists=True, dry_run=False)

@app.command("reset")
def reset():
    """Reset the project to the initial state"""
    clean.clean_all()

@app.command("cov")
def cov(
    path: str = "src/tidycode",
    html: bool = typer.Option(False, help="Generate an HTML report")
):
    """Run pytest with coverage."""
    command = ["pytest", f"--cov={path}", "--cov-report=term-missing"]
    if html:
        command.append("--cov-report=html")
    subprocess.run(command, check=True)

def main():
    app()


if __name__ == "__main__":
    main()
