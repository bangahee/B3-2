from __future__ import annotations

import ast
from pathlib import Path


FORBIDDEN_FUNCTIONS = {
    "sorted",
}

FORBIDDEN_METHODS = {
    "sort",
}

EXCLUDED_DIRECTORIES = {
    ".venv",
    "__pycache__",
    ".git",
}


def should_skip(path: Path) -> bool:
    """Return True when the file is inside an excluded directory."""

    return any(part in EXCLUDED_DIRECTORIES for part in path.parts)


def check_file(path: Path) -> list[str]:
    """
    Check one Python file for forbidden sorting API calls.

    Comments and docstrings are ignored because the Python AST only
    represents executable syntax.
    """

    problems: list[str] = []

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError) as error:
        problems.append(f"{path}: could not inspect file: {error}")
        return problems

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        # Detect calls such as:
        # sorted(items)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in FORBIDDEN_FUNCTIONS
        ):
            problems.append(
                f"{path}:{node.lineno} - forbidden call: "
                f"{node.func.id}()"
            )

        # Detect calls such as:
        # items.sort()
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in FORBIDDEN_METHODS
        ):
            problems.append(
                f"{path}:{node.lineno} - forbidden call: "
                f".{node.func.attr}()"
            )

    return problems


def main() -> None:
    """Inspect project Python files and print the constraint-check result."""

    project_root = Path(__file__).resolve().parent
    problems: list[str] = []
    checked_files = 0

    for path in project_root.rglob("*.py"):
        if should_skip(path):
            continue

        # Do not inspect this checker itself.
        if path.resolve() == Path(__file__).resolve():
            continue

        checked_files += 1
        problems.extend(check_file(path))

    print("Mini Git constraint check")
    print(f"Checked Python files: {checked_files}")

    if problems:
        print("\nFAIL: Forbidden sorting API usage found.")

        for problem in problems:
            print(f"- {problem}")

        raise SystemExit(1)

    print("\nPASS: No forbidden sorting API usage found.")
    print("- sorted() not used")
    print("- list.sort() / .sort() not used")
    print("- .venv, .git, and __pycache__ excluded")


if __name__ == "__main__":
    main()