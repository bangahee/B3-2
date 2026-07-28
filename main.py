from __future__ import annotations

import shlex

from mini_git import MiniGit


def execute_command(
    repository: MiniGit,
    command: str,
    args: list[str],
) -> str:
    """
    Validate a command and call the corresponding MiniGit method.
    """

    if command == "init":
        if len(args) != 1:
            return "Invalid args"

        return repository.init_repository(args[0])

    if command == "branch":
        if len(args) != 1:
            return "Invalid args"

        return repository.create_branch(args[0])

    if command == "switch":
        if len(args) != 1:
            return "Invalid args"

        return repository.switch_branch(args[0])

    if command == "commit":
        if len(args) != 1:
            return "Invalid args"

        return repository.create_commit(args[0])

    if command == "log":
        if len(args) == 0:
            return repository.show_log()

        if len(args) == 1:
            option = args[0]
            lower_option = option.lower()

            if lower_option.startswith("--sort-by="):
                sort_by = option.split("=", 1)[1].lower()
                return repository.show_sorted_log(sort_by)

        return "Invalid args"

    if command == "path":
        if len(args) != 2:
            return "Invalid args"

        return repository.show_path(
            start_hash=args[0],
            end_hash=args[1],
        )

    if command == "ancestors":
        if len(args) != 1:
            return "Invalid args"

        return repository.show_ancestors(args[0])

    if command == "search":
        if len(args) != 1:
            return "Invalid args"

        search_argument = args[0]
        lower_argument = search_argument.lower()

        if lower_argument.startswith("--author="):
            author = search_argument.split("=", 1)[1]
            return repository.search_author(author)

        return repository.search_keyword(search_argument)

    return f"Unknown command: {command}"


def main() -> None:
    """
    Run the Mini Git REPL until the user enters exit or quit.
    """

    repository = MiniGit()

    print("Mini Git")
    print("Enter 'exit' or 'quit' to close the program.")

    while True:
        try:
            raw_command = input("mini-git> ").strip()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nUse exit or quit to close Mini Git.")
            continue

        if not raw_command:
            continue

        try:
            parts = shlex.split(raw_command)
        except ValueError:
            # This can happen when quotation marks are not closed.
            print("Invalid args")
            continue

        if not parts:
            continue

        command = parts[0].lower()
        args = parts[1:]

        if command in ("exit", "quit"):
            print("Mini Git closed.")
            break

        result = execute_command(
            repository=repository,
            command=command,
            args=args,
        )

        print(result)


if __name__ == "__main__":
    main()