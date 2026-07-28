from __future__ import annotations

from collections import deque

from models.commit import Commit


def topological_commit_order(
    commits: dict[str, Commit],
) -> list[str]:
    """
    Return commit hashes in parent-before-child order.

    This uses a depth-first search approach. Before a commit is added to
    the result, all of its parent commits are visited first.

    Time complexity:
        O(V + E)

    V:
        Number of commits.

    E:
        Number of parent-child connections.
    """

    visited: set[str] = set()
    result: list[str] = []

    for commit_hash in commits:
        _visit_commit_for_log(
            commit_hash=commit_hash,
            commits=commits,
            visited=visited,
            result=result,
        )

    return result


def _visit_commit_for_log(
    commit_hash: str,
    commits: dict[str, Commit],
    visited: set[str],
    result: list[str],
) -> None:
    """
    Visit every parent before adding the current commit to the result.
    """

    if commit_hash in visited:
        return

    visited.add(commit_hash)

    commit = commits[commit_hash]

    for parent_hash in commit.parents:
        if parent_hash in commits:
            _visit_commit_for_log(
                commit_hash=parent_hash,
                commits=commits,
                visited=visited,
                result=result,
            )

    result.append(commit_hash)


def find_all_ancestors(
    commit_hash: str,
    commits: dict[str, Commit],
) -> list[str]:
    """
    Return all ancestors of a commit in parent-before-child order.

    The selected commit itself is not included.

    Time complexity:
        O(V + E) for the reachable ancestor graph.
    """

    visited: set[str] = set()
    result: list[str] = []

    commit = commits[commit_hash]

    for parent_hash in commit.parents:
        _visit_ancestor(
            commit_hash=parent_hash,
            commits=commits,
            visited=visited,
            result=result,
        )

    return result


def _visit_ancestor(
    commit_hash: str,
    commits: dict[str, Commit],
    visited: set[str],
    result: list[str],
) -> None:
    """
    Recursively visit older ancestors before adding the current ancestor.
    """

    if commit_hash in visited:
        return

    visited.add(commit_hash)

    commit = commits[commit_hash]

    for parent_hash in commit.parents:
        if parent_hash in commits:
            _visit_ancestor(
                commit_hash=parent_hash,
                commits=commits,
                visited=visited,
                result=result,
            )

    result.append(commit_hash)


def find_shortest_path(
    start_hash: str,
    end_hash: str,
    commits: dict[str, Commit],
    children: dict[str, list[str]],
) -> list[str] | None:
    """
    Find a shortest path between two commits using BFS.

    Parent-child connections are treated as undirected connections.
    Therefore, traversal can move from a child to a parent and from a
    parent to a child.

    When multiple shortest paths exist, this function returns the path
    whose full hash string is lexicographically smallest.

    Example comparison:
        aaa111->bbb222->ddd444
        aaa111->ccc333->ddd444

    The first path is selected because its string comes first
    lexicographically.
    """

    if start_hash == end_hash:
        return [start_hash]

    queue: deque[list[str]] = deque()
    queue.append([start_hash])

    shortest_paths: list[list[str]] = []
    shortest_distance: int | None = None

    # Stores the smallest distance at which each commit was reached.
    best_distance: dict[str, int] = {
        start_hash: 0,
    }

    while queue:
        current_path = queue.popleft()
        current_hash = current_path[-1]
        current_distance = len(current_path) - 1

        if (
            shortest_distance is not None
            and current_distance > shortest_distance
        ):
            continue

        if current_hash == end_hash:
            shortest_distance = current_distance
            shortest_paths.append(current_path)
            continue

        neighbors = _get_neighbors(
            commit_hash=current_hash,
            commits=commits,
            children=children,
        )

        for neighbor_hash in neighbors:
            # Prevent cycles inside the current path.
            if neighbor_hash in current_path:
                continue

            next_distance = current_distance + 1

            previous_distance = best_distance.get(neighbor_hash)

            if (
                previous_distance is None
                or next_distance <= previous_distance
            ):
                best_distance[neighbor_hash] = next_distance
                queue.append(current_path + [neighbor_hash])

    if not shortest_paths:
        return None

    return _find_lexicographically_smallest_path(shortest_paths)


def _get_neighbors(
    commit_hash: str,
    commits: dict[str, Commit],
    children: dict[str, list[str]],
) -> list[str]:
    """
    Return the parent and child neighbours of one commit.
    """

    neighbors: list[str] = []

    commit = commits[commit_hash]

    for parent_hash in commit.parents:
        if parent_hash in commits:
            neighbors.append(parent_hash)

    for child_hash in children.get(commit_hash, []):
        if child_hash in commits:
            neighbors.append(child_hash)

    return neighbors


def _find_lexicographically_smallest_path(
    paths: list[list[str]],
) -> list[str]:
    """
    Select the lexicographically smallest path without using sorting APIs.
    """

    smallest_path = paths[0]
    smallest_text = "->".join(smallest_path)

    for path in paths[1:]:
        path_text = "->".join(path)

        if path_text < smallest_text:
            smallest_path = path
            smallest_text = path_text

    return smallest_path