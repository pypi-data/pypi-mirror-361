"""
Base class for YAML adapters.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class YAMLAdapter(ABC):
    """Interface for a YAML adapter (PyYAML, ruamel, etc)."""

    @abstractmethod
    def load_str(self, content: str) -> Any:
        """Load a YAML string into a Python object."""
        pass

    @abstractmethod
    def dump_str(self, data: Any) -> str:
        """Dump a Python object into a YAML string."""
        pass

    @abstractmethod
    def load_file(self, path: Path) -> Any:
        """Load a YAML file into a Python object."""
        pass

    @abstractmethod
    def save_file(self, data: Any, path: Path) -> None:
        """Save a Python object to a YAML file."""
        pass
