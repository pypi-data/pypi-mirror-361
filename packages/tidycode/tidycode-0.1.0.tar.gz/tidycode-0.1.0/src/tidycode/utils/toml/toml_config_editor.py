"""
Editor for toml files
"""

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from tomlkit import table

from .toml_config_diff import diff_configs, format_config_diff
from .toml_helpers import PYPROJECT_PATH, load_toml_file, save_toml_file


def inject_toml_config(
    base: Dict[str, Any],
    new_data: Dict[str, Any],
    overwrite: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Inject a configuration into the existing TOML content.
    Inject potentially multiple configurations into the tool key of a new_data dict.

    It reads the tool key in new_data["tool"] with potentially multiple tools (sections),
    and injects each of these sections into updated["tool"].

    - `overwrite=False` will raise an error if the section exists.
    - `dry_run=True` does not modify the content, but returns the theoretical result.
    """
    updated = deepcopy(base)
    tool_data = new_data.get("tool", {})

    if "tool" not in updated:
        updated["tool"] = table()

    for section, value in tool_data.items():
        if section in updated["tool"] and not overwrite:
            raise ValueError(f"[tool.{section}] already exists in toml file")
        updated["tool"][section] = value

    if dry_run:
        diff = diff_configs(base, updated)
        output = format_config_diff(diff)
        print(output)

    return updated


def inject_tool_config(
    base: Dict[str, Any],
    tool_name: str,
    tool_config: Dict[str, Any],
    overwrite: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Inject the config for a tool in the [tool.<tool_name>] section of toml file.

    - overwrite=False will raise an error if the config exists.
    - dry_run=True will print the diff without modifying the config.
    """
    updated = deepcopy(base)

    if "tool" not in updated:
        updated["tool"] = table()

    if tool_name in updated["tool"] and not overwrite:
        raise ValueError(f"[tool.{tool_name}] already exists in toml file")

    updated["tool"][tool_name] = tool_config

    if dry_run:
        diff = diff_configs(base, updated)
        print(format_config_diff(diff))

    return updated


def merge_dict_minimal(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Add only keys absent from update, without overwriting."""
    merged = deepcopy(base)

    for k, v in update.items():
        if k not in merged:
            merged[k] = v
    return merged


def inject_tool_config_in_file(
    toml_file_path: Path,
    tool_name: str,
    config: Dict[str, Any],  # doit contenir {"tool": {tool_name: {...}}}
    update_if_exists: bool = False,
    dry_run: bool = False,
) -> None:
    """
    Injecte une config complète [tool.<tool_name>] dans pyproject.toml.

    Ex:
        inject_tool_config_in_file(pyproject, "black", black_config["pyproject_config"])
    """
    toml_file_path = toml_file_path or PYPROJECT_PATH
    toml_data = load_toml_file(toml_file_path)
    tool_config = config.get("tool", {}).get(tool_name)

    if tool_config is None:
        raise ValueError("Invalid config format: missing 'tool.<tool_name>' section")

    existing_section = toml_data.get("tool", {}).get(tool_name)

    if existing_section is not None:
        if update_if_exists:
            merged = merge_dict_minimal(existing_section, tool_config)
            config = {"tool": {tool_name: merged}}
            updated = inject_toml_config(toml_data, config, overwrite=True)
        else:
            raise ValueError(
                f"[tool.{tool_name}] already exists in {toml_file_path}. "
                f"Pass update_if_exists=True to merge."
            )
    else:
        updated = inject_toml_config(toml_data, config, overwrite=False)

    diff = diff_configs(toml_data, updated)

    if dry_run:
        print(format_config_diff(diff))
    else:
        if diff:
            save_toml_file(updated, toml_file_path)
            print(f"[tool.{tool_name}] injected/updated in {toml_file_path}")
        else:
            print(f"No change for [tool.{tool_name}] in {toml_file_path}")
