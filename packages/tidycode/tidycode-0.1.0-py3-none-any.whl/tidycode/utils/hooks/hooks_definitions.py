"""
Hook definitions
"""

HOOKS = {
    "pre-commit": {
        "name": "Pre-commit",
        "yaml": {
            "repo": "https://github.com/pre-commit/pre-commit-hooks",
            "rev": "v5.0.0",
            "hooks": [
                {"id": "trailing-whitespace"},
                {"id": "end-of-file-fixer"},
                {"id": "check-yaml"},
                {"id": "check-added-large-files"},
            ],
        },
    },
    "commitizen": {
        "name": "Commitizen (conventional commits)",
        "yaml": {
            "repo": "https://github.com/commitizen-tools/commitizen",
            "rev": "v4.8.3",
            "hooks": [
                {"id": "commitizen"},
                {
                    "id": "commitizen-branch",
                    "stages": ["pre-push"],
                },
            ],
        },
    },
    # "commitizen-message": {
    #     "name": "Commitizen Message",
    #     "yaml": {
    #         "repo": "local",
    #         "hooks": [
    #             {
    #                 "id": "commitizen-message-check",
    #                 "name": "Commitizen message check",
    #                 "entry": "cz check -- --commit-msg-file",
    #                 "language": "system",
    #                 "stages": ["[commit-msg]"],
    #                 "args": ["{commit_msg_file}"],
    #             }
    #         ],
    #     },
    # },
    "format_black": {
        "name": "Black Formatter",
        "yaml": {
            "repo": "https://github.com/psf/black",
            "rev": "25.1.0",
            "hooks": [
                {
                    "id": "black",
                    "language_version": "python3",
                },
            ],
        },
    },
    "linting": {
        "name": "Ruff Linter",
        "yaml": {
            "repo": "https://github.com/astral-sh/ruff-pre-commit",
            "rev": "v0.12.1",
            "hooks": [
                {
                    "id": "ruff",
                    "args": ["--fix"],
                    "language_version": "python3",
                    "files": r"\.py$",
                },
            ],
        },
    },
    "format_isort": {
        "name": "isort Import Sorter",
        "yaml": {
            "repo": "https://github.com/pre-commit/mirrors-isort",
            "rev": "v5.13.2",
            "hooks": [{"id": "isort"}],
        },
    },
}
