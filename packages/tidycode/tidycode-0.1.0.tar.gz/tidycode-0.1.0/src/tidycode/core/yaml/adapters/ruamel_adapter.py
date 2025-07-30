"""
Adapter for ruamel.yaml.
"""

from io import StringIO
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML, CommentedSeq

from .base import YAMLAdapter


class RuamelYAMLAdapter(YAMLAdapter):
    """Adapter for ruamel.yaml."""

    def __init__(self):
        self.yaml = YAML()
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False

    def load_str(self, content: str) -> Any:
        return self.yaml.load(content)

    def dump_str(self, data: Any) -> str:
        stream = StringIO()
        self.yaml.dump(data, stream)
        return stream.getvalue()

    def load_file(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as f:
            return self.yaml.load(f)

    def save_file(self, data: Any, path: Path) -> None:
        self._format_hooks_spacing(data)
        with path.open("w", encoding="utf-8") as f:
            self.yaml.dump(data, f)

    def _format_hooks_spacing(self, data: Any) -> None:
        """
        Add a blank line between each repo in 'repos'.
        """
        if not isinstance(data, dict):
            return

        repos = data.get("repos")
        if not isinstance(repos, list):
            return

        if isinstance(repos, CommentedSeq):
            for i in range(len(repos) - 1):
                repos.yaml_set_comment_before_after_key(i + 1, before="\n", after="\n")
