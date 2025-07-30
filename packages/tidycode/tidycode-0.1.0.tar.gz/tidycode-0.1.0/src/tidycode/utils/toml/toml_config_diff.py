"""
Compare two TOML files and return a list of differences.
"""

from typing import Any, Dict, List, Tuple


def diff_configs(
    old: Dict[str, Any], new: Dict[str, Any]
) -> List[Tuple[str, str, Any, Any]]:
    """
    Compare the configurations in the [tool.*] section and return a list
    of tuples (type, section, old_value, new_value).

    type can be 'added', 'removed', 'changed'.
    """
    diffs = []

    old_tools = old.get("tool", {})
    new_tools = new.get("tool", {})

    all_keys = set(old_tools.keys()) | set(new_tools.keys())

    for key in sorted(all_keys):
        old_val = old_tools.get(key)
        new_val = new_tools.get(key)

        if old_val is None and new_val is not None:
            diffs.append(("added", key, None, new_val))
        elif old_val is not None and new_val is None:
            diffs.append(("removed", key, old_val, None))
        elif old_val != new_val:
            diffs.append(("changed", key, old_val, new_val))

    return diffs


def format_config_diff(diff: List[Tuple[str, str, Any, Any]]) -> str:
    """
    Format the list of differences into a readable text.
    """
    lines = []
    for change_type, section, old_val, new_val in diff:
        if change_type == "added":
            lines.append(f"+ [tool.{section}]")
            for k, v in new_val.items():
                lines.append(f"+ {k} = {repr(v)}")
        elif change_type == "removed":
            lines.append(f"- [tool.{section}]")
        elif change_type == "changed":
            lines.append(f"~ [tool.{section}]")
            for k in sorted(set(old_val.keys()) | set(new_val.keys())):
                old_v = old_val.get(k)
                new_v = new_val.get(k)
                if old_v != new_v:
                    lines.append(f"~ {k}: {old_v!r} → {new_v!r}")
    return "\n".join(lines)
