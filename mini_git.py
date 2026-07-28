from __future__ import annotations

import hashlib
from datetime import datetime

from algorithms.graph import (
    find_all_ancestors,
    find_shortest_path,
    topological_commit_order,
)
from algorithms.sorting import merge_sort
from models.commit import Commit


class MiniGit:
    """
    Stores Mini Git repository data and implements repository commands.
    """

    def __init__(self) -> None:
        # commit hash -> Commit object
        self.commits: dict[str, Commit] = {}

        # branch name -> branch HEAD commit hash
        self.branches: dict[str, str | None] = {}

        # Name of the branch currently selected by HEAD.
        self.current_branch: str | None = None

        # Author name used when creating commits.
        self.current_user: str | None = None

        # keyword -> commit hash list
        self.keyword_index: dict[str, list[str]] = {}

        # lower-case author name -> commit hash list
        self.author_index: dict[str, list[str]] = {}

        # parent commit hash -> child commit hash list
        self.children: dict[str, list[str]] = {}

        # Used as part of commit hash generation.
        self.commit_counter = 0

        self.initialized = False

    def init_repository(self, user_name: str) -> str:
        """
        Initialise an empty repository.

        INIT creates the main branch, selects it as the current branch,
        and stores the current user.
        """

        user_name = user_name.strip()

        if not user_name:
            return "Invalid args"

        self.commits = {}
        self.branches = {
            "main": None,
        }
        self.current_branch = "main"
        self.current_user = user_name

        self.keyword_index = {}
        self.author_index = {}
        self.children = {}

        self.commit_counter = 0
        self.initialized = True

        return (
            "Initialized repository.\n"
            "Current branch: main\n"
            f"Current user: {self.current_user}"
        )

    def create_branch(self, branch_name: str) -> str:
        """
        Create a new branch pointing to the current branch's HEAD.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        branch_name = branch_name.strip()

        if not branch_name:
            return "Invalid args"

        if branch_name in self.branches:
            return f"Branch already exists: {branch_name}"

        current_head = self.branches[self.current_branch]

        self.branches[branch_name] = current_head

        return f"Created branch: {branch_name}"

    def switch_branch(self, branch_name: str) -> str:
        """
        Move HEAD to an existing branch.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        branch_name = branch_name.strip()

        if not branch_name:
            return "Invalid args"

        if branch_name not in self.branches:
            return f"Unknown branch: {branch_name}"

        self.current_branch = branch_name

        return f"Switched to branch: {branch_name}"

    def create_commit(self, message: str) -> str:
        """
        Create a new commit on the current branch.

        The previous branch HEAD becomes the parent of the new commit.
        The branch HEAD then moves to the new commit.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        message = message.strip()

        if not message:
            return "Invalid args"

        timestamp = datetime.now()

        current_head = self.branches[self.current_branch]

        parents: list[str] = []

        if current_head is not None:
            parents.append(current_head)

        commit_hash = self._generate_commit_hash(
            message=message,
            author=self.current_user,
            timestamp=timestamp,
        )

        commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.current_user,
            timestamp=timestamp,
            parents=parents,
        )

        # Store the commit for average O(1) hash lookup.
        self.commits[commit_hash] = commit

        # Move the current branch HEAD to the new commit.
        self.branches[self.current_branch] = commit_hash

        # Prepare an empty child list for the new commit.
        if commit_hash not in self.children:
            self.children[commit_hash] = []

        # Register the new commit as a child of each parent.
        for parent_hash in parents:
            if parent_hash not in self.children:
                self.children[parent_hash] = []

            self.children[parent_hash].append(commit_hash)

        # Update the keyword and author inverted indexes.
        self._update_indexes(commit)

        return (
            f"[{self.current_branch} {commit.hash}] "
            f"{commit.message}"
        )

    def show_log(self) -> str:
        """
        Display all commits in parent-before-child order.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        if not self.commits:
            return "No commits"

        ordered_hashes = topological_commit_order(self.commits)

        output: list[str] = []

        for commit_hash in ordered_hashes:
            commit = self.commits[commit_hash]
            output.append(self._format_commit(commit))

        return "\n\n".join(output)

    def show_sorted_log(self, sort_by: str) -> str:
        """
        Display commits sorted by date or author using manual merge sort.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        if not self.commits:
            return "No commits"

        commits = list(self.commits.values())

        if sort_by == "date":
            ordered_commits = merge_sort(
                commits,
                self._date_before_or_equal,
            )
        elif sort_by == "author":
            ordered_commits = merge_sort(
                commits,
                self._author_before_or_equal,
            )
        else:
            return "Invalid args"

        output: list[str] = []

        for commit in ordered_commits:
            output.append(self._format_commit(commit))

        return "\n\n".join(output)

    def show_path(
        self,
        start_hash: str,
        end_hash: str,
    ) -> str:
        """
        Display the shortest path between two commits.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        if start_hash not in self.commits:
            return f"Unknown commit: {start_hash}"

        if end_hash not in self.commits:
            return f"Unknown commit: {end_hash}"

        path = find_shortest_path(
            start_hash=start_hash,
            end_hash=end_hash,
            commits=self.commits,
            children=self.children,
        )

        if path is None:
            return "No path"

        return f"Path: {' -> '.join(path)}"

    def show_ancestors(self, commit_hash: str) -> str:
        """
        Display all ancestors of one commit.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        if commit_hash not in self.commits:
            return f"Unknown commit: {commit_hash}"

        ancestor_hashes = find_all_ancestors(
            commit_hash=commit_hash,
            commits=self.commits,
        )

        if not ancestor_hashes:
            return "No ancestors"

        output: list[str] = []

        for ancestor_hash in ancestor_hashes:
            ancestor = self.commits[ancestor_hash]
            output.append(self._format_commit(ancestor))

        return "\n\n".join(output)

    def search_keyword(self, keyword: str) -> str:
        """
        Search commits using the keyword inverted index.

        A quoted multi-word query is supported. For example:

            SEARCH "login feature"

        The commit must contain all query tokens.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        query_tokens = keyword.strip().lower().split()

        if not query_tokens:
            return "Invalid args"

        first_token = query_tokens[0]

        if first_token not in self.keyword_index:
            return "Found 0 commits"

        # Preserve the original commit creation order from the first token.
        candidate_hashes = self.keyword_index[first_token][:]

        for token in query_tokens[1:]:
            matching_hashes = self.keyword_index.get(token)

            if matching_hashes is None:
                return "Found 0 commits"

            matching_set = set(matching_hashes)
            filtered_candidates: list[str] = []

            for commit_hash in candidate_hashes:
                if commit_hash in matching_set:
                    filtered_candidates.append(commit_hash)

            candidate_hashes = filtered_candidates

            if not candidate_hashes:
                return "Found 0 commits"

        return self._format_search_results(candidate_hashes)

    def search_author(self, author: str) -> str:
        """
        Search commits using the author inverted index.
        """

        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        author_key = author.strip().lower()

        if not author_key:
            return "Invalid args"

        commit_hashes = self.author_index.get(author_key, [])

        if not commit_hashes:
            return "Found 0 commits"

        return self._format_search_results(commit_hashes)

    def _get_repository_error(self) -> str | None:
        """
        Return an error message when INIT has not been executed.
        """

        if not self.initialized:
            return "Repository not initialized"

        return None

    def _generate_commit_hash(
        self,
        message: str,
        author: str,
        timestamp: datetime,
    ) -> str:
        """
        Generate a session-unique six-character commit hash.

        A counter is included in the source text so every generation attempt
        has different input. The result is also checked against existing
        commit hashes to guarantee that duplicates are not accepted.
        """

        while True:
            self.commit_counter += 1

            source_text = (
                f"{self.commit_counter}|"
                f"{message}|"
                f"{author}|"
                f"{timestamp.isoformat()}"
            )

            full_hash = hashlib.sha1(
                source_text.encode("utf-8")
            ).hexdigest()

            commit_hash = full_hash[:6]

            if commit_hash not in self.commits:
                return commit_hash

    def _update_indexes(self, commit: Commit) -> None:
        """
        Add a commit to the author and keyword inverted indexes.
        """

        author_key = commit.author.lower()

        if author_key not in self.author_index:
            self.author_index[author_key] = []

        self.author_index[author_key].append(commit.hash)

        message_tokens = commit.message.lower().split()

        # Prevent the same commit from being indexed repeatedly when its
        # message contains the same word more than once.
        added_tokens: set[str] = set()

        for token in message_tokens:
            if token in added_tokens:
                continue

            if token not in self.keyword_index:
                self.keyword_index[token] = []

            self.keyword_index[token].append(commit.hash)
            added_tokens.add(token)

    def _branch_labels(self, commit_hash: str) -> list[str]:
        """
        Return branch names currently pointing to the given commit.
        """

        labels: list[str] = []

        for branch_name, branch_head in self.branches.items():
            if branch_head == commit_hash:
                labels.append(branch_name)

        return labels

    def _format_commit(self, commit: Commit) -> str:
        """
        Convert one Commit object into readable terminal output.
        """

        timestamp_text = commit.timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        branch_labels = self._branch_labels(commit.hash)

        branch_text = ""

        if branch_labels:
            branch_text = f" [{', '.join(branch_labels)}]"

        return (
            f"commit {commit.hash} "
            f"({commit.author}, {timestamp_text})"
            f"{branch_text}\n"
            f"{commit.message}"
        )

    def _format_search_results(
        self,
        commit_hashes: list[str],
    ) -> str:
        """
        Format keyword or author search results.
        """

        output = [
            f"Found {len(commit_hashes)} commit(s):",
        ]

        for commit_hash in commit_hashes:
            commit = self.commits[commit_hash]

            output.append(
                f"- {commit.hash}: "
                f"{commit.message} "
                f"({commit.author})"
            )

        return "\n".join(output)

    @staticmethod
    def _date_before_or_equal(
        first: Commit,
        second: Commit,
    ) -> bool:
        """
        Compare commits by timestamp.

        Hash is used as a deterministic tie-breaker.
        """

        if first.timestamp == second.timestamp:
            return first.hash <= second.hash

        return first.timestamp < second.timestamp

    @staticmethod
    def _author_before_or_equal(
        first: Commit,
        second: Commit,
    ) -> bool:
        """
        Compare commits by author.

        Timestamp and hash are used as tie-breakers.
        """

        first_author = first.author.lower()
        second_author = second.author.lower()

        if first_author != second_author:
            return first_author < second_author

        if first.timestamp != second.timestamp:
            return first.timestamp < second.timestamp

        return first.hash <= second.hash