"""
Utils for Tidycode
"""

from .constants import (
    CONFIG_FILE_PATH,
    DEPENDABOT_PATH,
    EXCLUDE_DIRS,
    PYPROJECT_PATH,
    TARGETS,
)
from .helpers import (
    ask_checkbox,
    ask_confirm,
    print_msg,
    run_command,
    write_file_if_missing,
    yaml_dump,
    yaml_load,
)
from .hooks.hooks_definitions import HOOKS
from .hooks.hooks_helpers import (
    add_hooks,
    get_hooks_with_yaml,
    get_installed_hook_keys,
    get_iter_hook_with_yaml,
    remove_hooks,
)
from .toml.toml_config_diff import diff_configs, format_config_diff
from .toml.toml_config_editor import (
    inject_toml_config,
    inject_tool_config,
    inject_tool_config_in_file,
)
from .toml.toml_helpers import (
    get_tool_section,
    has_tool_section,
    load_toml_file,
    remove_tool_section,
    remove_tool_section_and_return,
    save_toml_file,
    set_tool_section,
    toml_dump,
    toml_load,
)
from .tools_metadata import TOOLS_METADATA

__all__ = [
    "CONFIG_FILE_PATH",
    "PYPROJECT_PATH",
    "DEPENDABOT_PATH",
    "TOOLS_METADATA",
    "HOOKS",
    "EXCLUDE_DIRS",
    "TARGETS",
    "get_installed_hook_keys",
    "add_hooks",
    "remove_hooks",
    "get_hooks_with_yaml",
    "get_iter_hook_with_yaml",
    "run_command",
    "write_file_if_missing",
    "ask_checkbox",
    "ask_confirm",
    "print_msg",
    "yaml_dump",
    "yaml_load",
    "toml_dump",
    "toml_load",
    "load_toml_file",
    "save_toml_file",
    "has_tool_section",
    "get_tool_section",
    "set_tool_section",
    "remove_tool_section",
    "remove_tool_section_and_return",
    "inject_toml_config",
    "inject_tool_config",
    "inject_tool_config_in_file",
    "diff_configs",
    "format_config_diff",
]
