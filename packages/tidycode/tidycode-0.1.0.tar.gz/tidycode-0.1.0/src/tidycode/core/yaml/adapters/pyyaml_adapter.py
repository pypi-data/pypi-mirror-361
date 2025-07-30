"""
Adapter for PyYAML.
"""

from pathlib import Path
from typing import Any

import yaml

from .base import YAMLAdapter


class PyYAMLAdapter(YAMLAdapter):
    """Adapter for PyYAML."""

    def load_str(self, content: str) -> Any:
        return yaml.safe_load(content)

    def dump_str(self, data: Any) -> str:
        return yaml.safe_dump(data, sort_keys=False)

    def load_file(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save_file(self, data: Any, path: Path) -> None:
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)
