"""
Helpers for hooks
"""

from typing import Iterator

from .hooks_definitions import HOOKS


def get_installed_hook_keys(config: dict) -> list[str]:
    """Get the installed hook keys from the config."""
    installed_keys = []
    for repo in config.get("repos", []):
        for key, hook in HOOKS.items():
            if "yaml" in hook and hook["yaml"]["repo"] == repo.get("repo"):
                installed_keys.append(key)
    return installed_keys


def add_hooks(config: dict, keys: list[str]) -> dict:
    """Add the hooks to the config."""
    for key in keys:
        hook = HOOKS[key]
        repo = hook["yaml"]
        if not any(r["repo"] == repo["repo"] for r in config.get("repos", [])):
            config["repos"].append(repo)
    return config


def remove_hooks(config: dict, keys: list[str]) -> dict:
    """Remove the hooks from the config."""
    repos_to_remove = [HOOKS[k]["yaml"]["repo"] for k in keys if "yaml" in HOOKS[k]]
    config["repos"] = [
        r for r in config.get("repos", []) if r.get("repo") not in repos_to_remove
    ]
    return config


def get_hooks_with_yaml() -> list[str]:
    """Get a list of the hooks with yaml."""
    return [k for k, v in HOOKS.items() if "yaml" in v]


def get_iter_hook_with_yaml() -> Iterator[str]:
    """Get an iterator over the hooks with yaml."""
    return next(k for k, v in HOOKS.items() if "yaml" in v)
