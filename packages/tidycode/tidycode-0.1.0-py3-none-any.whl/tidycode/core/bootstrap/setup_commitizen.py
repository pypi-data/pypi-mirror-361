"""
Setup Commitizen
"""

from pathlib import Path
from typing import Callable

from tidycode.utils import (
    PYPROJECT_PATH,
    TOOLS_METADATA,
    get_tool_section,
    inject_toml_config,
    load_toml_file,
    run_command,
    save_toml_file,
)


def setup_commitizen(
    pyproject_path: Path = None,
    dry_run: bool = False,
    run_command_fn: Callable = None,
) -> bool:
    """
    Injects Commitizen configuration into pyproject.toml and runs cz init.
    """
    pyproject_path = pyproject_path or PYPROJECT_PATH
    run_command_fn = run_command_fn or run_command

    if not pyproject_path.exists():
        print(f"❌ {pyproject_path} not found")
        return False

    pyproject_data = load_toml_file(pyproject_path)

    # Skip if already present
    if get_tool_section(pyproject_data, "commitizen") is not None:
        print("⚠️ Commitizen already present in pyproject.toml")
        return False

    # Inject configuration
    new_config = TOOLS_METADATA["commitizen"]["pyproject_config"]
    updated = inject_toml_config(pyproject_data, new_config, dry_run=dry_run)

    if dry_run:
        print("🧪 Dry run enabled. Showing what would change: \n")
        from tidycode.utils import diff_configs, format_config_diff

        diffs = diff_configs(pyproject_data, updated)
        print(format_config_diff(diffs))
        return True

    # Save
    save_toml_file(updated, pyproject_path)
    print("✅ Commitizen config added to pyproject.toml")

    try:
        run_command_fn(
            ["cz", "init", "--", "--name", "cz_conventional_commits", "--yes"]
        )
    except Exception as e:
        print(f"⚠️ Commitizen CLI init failed: {e}")

    return True
