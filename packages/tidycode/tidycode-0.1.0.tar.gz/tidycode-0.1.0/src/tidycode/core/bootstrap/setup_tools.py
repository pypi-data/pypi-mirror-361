# tidycode/core/bootstrap.py

from pathlib import Path

from tidycode.utils import TOOLS_METADATA, inject_tool_config_in_file


def setup_tool_from_metadata(
    key: str,
    pyproject_path: Path,
    update_if_exists: bool = False,
    dry_run: bool = False,
) -> bool:
    """
    Inject tool config into pyproject.toml based on metadata key.

    Args:
        key (str): tool_metadata key (e.g., "format_black")
        pyproject_path (Path): path to pyproject.toml
        update_if_exists (bool): if True, merge config
        dry_run (bool): preview only

    Returns:
        bool: success
    """
    if not pyproject_path.exists():
        print(f"❌ File not found: {pyproject_path}")
        return False

    meta = TOOLS_METADATA.get(key)
    if not meta or "pyproject_config" not in meta:
        print(f"❌ No pyproject_config found in tool metadata for '{key}'")
        return False

    config = meta["pyproject_config"]

    try:
        inject_tool_config_in_file(
            toml_file_path=pyproject_path,
            tool_name=key,
            config=config,
            update_if_exists=update_if_exists,
            dry_run=dry_run,
        )
        return True
    except ValueError as e:
        print(f"⚠️ {e}")
        return False
