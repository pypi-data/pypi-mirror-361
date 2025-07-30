"""
Manager for YAML files.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from tidycode.utils import CONFIG_FILE_PATH

from .adapters.base import YAMLAdapter
from .adapters.ruamel_adapter import RuamelYAMLAdapter


class YAMLManager:
    """Manager for YAML files."""

    def __init__(self, adapter: Optional[YAMLAdapter] = None):
        self.adapter = adapter or RuamelYAMLAdapter()

    def set_adapter(self, adapter: YAMLAdapter) -> None:
        self.adapter = adapter

    def load_str(self, content: str) -> Dict[str, Any]:
        return self.adapter.load_str(content)

    def dump_str(self, data: Dict[str, Any]) -> str:
        return self.adapter.dump_str(data)

    def load_file(self, path: Optional[Path] = None) -> Dict[str, Any]:
        path = path or CONFIG_FILE_PATH

        if not path.exists():
            return {"repos": []}

        data = self.adapter.load_file(path)

        if data is None:
            return {"repos": []}
        return data

    def save_file(self, data: Dict[str, Any], path: Optional[Path] = None) -> None:
        path = path or CONFIG_FILE_PATH
        self.adapter.save_file(data, path)
