from __future__ import annotations

# BFS에서 사용할 큐 자료구조를 가져온다.
# deque는 리스트의 pop(0)보다 앞쪽 원소 제거가 효율적이다.
from collections import deque

# 커밋 노드의 자료형을 사용하기 위해 Commit 클래스를 가져온다.
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

    # 이미 방문한 커밋을 저장한다.
    # 같은 커밋을 여러 번 탐색하거나 출력하는 것을 방지한다.
    visited: set[str] = set()

    # 부모가 자식보다 먼저 배치된 commit hash 목록을 저장한다.
    result: list[str] = []

    # commits 딕셔너리에 저장된 모든 커밋을 확인한다.
    #
    # 브랜치가 분리된 경우 하나의 시작점만 탐색하면
    # 일부 커밋을 방문하지 못할 수 있으므로 모든 커밋을 시작점 후보로 확인한다.
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

    # 이미 방문한 커밋이면 다시 탐색하지 않는다.
    #
    # merge 형태처럼 여러 경로에서 같은 부모에 도달하더라도
    # 같은 커밋이 중복 출력되는 것을 방지한다.
    if commit_hash in visited:
        return

    # 현재 커밋을 방문 처리한다.
    visited.add(commit_hash)

    # hash를 key로 사용하여 Commit 객체를 빠르게 조회한다.
    commit = commits[commit_hash]

    # 현재 커밋을 결과에 추가하기 전에 모든 부모를 먼저 방문한다.
    #
    # 이 순서 때문에 부모 커밋이 자식 커밋보다 항상 먼저 출력된다.
    for parent_hash in commit.parents:
        if parent_hash in commits:
            _visit_commit_for_log(
                commit_hash=parent_hash,
                commits=commits,
                visited=visited,
                result=result,
            )

    # 부모 방문이 끝난 뒤 현재 커밋을 결과에 추가한다.
    #
    # 예:
    # A <- B <- C
    #
    # C에서 시작하면 A, B, C 순서로 result에 들어간다.
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

    # 이미 확인한 조상 커밋을 저장한다.
    # 같은 조상이 여러 부모 경로를 통해 발견되어도 한 번만 처리한다.
    visited: set[str] = set()

    # 최종적으로 출력할 조상 commit hash 목록이다.
    result: list[str] = []

    # 탐색을 시작할 대상 커밋을 조회한다.
    commit = commits[commit_hash]

    # 대상 커밋 자신은 조상이 아니므로 result에 넣지 않는다.
    #
    # 대신 대상 커밋의 부모들부터 조상 탐색을 시작한다.
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

    # 이미 방문한 조상이면 중복 탐색하지 않는다.
    if commit_hash in visited:
        return

    # 현재 조상을 방문 처리한다.
    visited.add(commit_hash)

    # 현재 조상 커밋 객체를 조회한다.
    commit = commits[commit_hash]

    # 현재 조상을 result에 추가하기 전에,
    # 더 오래된 부모 조상들을 먼저 방문한다.
    #
    # 따라서 결과는 가능한 한 오래된 조상부터 출력된다.
    for parent_hash in commit.parents:
        if parent_hash in commits:
            _visit_ancestor(
                commit_hash=parent_hash,
                commits=commits,
                visited=visited,
                result=result,
            )

    # 더 오래된 부모 조상 방문이 끝난 후 현재 조상을 추가한다.
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

    # 시작 커밋과 도착 커밋이 같으면 이동할 필요가 없다.
    #
    # 간선 수 0인 경로가 최단 경로이므로 시작 커밋 하나만 반환한다.
    if start_hash == end_hash:
        return [start_hash]

    # BFS에서 사용할 큐이다.
    #
    # 큐에는 현재 commit hash 하나만 저장하는 것이 아니라,
    # 시작점부터 현재 위치까지의 전체 경로를 저장한다.
    #
    # 예:
    # ["A", "B", "C"]
    queue: deque[list[str]] = deque()

    # 시작 경로를 큐에 추가한다.
    queue.append([start_hash])

    # 발견한 모든 최단 경로를 저장한다.
    #
    # 요구사항상 최단 경로가 여러 개라면
    # 그중 사전순으로 가장 작은 경로를 선택해야 한다.
    shortest_paths: list[list[str]] = []

    # 현재까지 발견된 최단 거리이다.
    #
    # 아직 목적지에 도달하지 못한 상태에서는 None이다.
    shortest_distance: int | None = None

    # 각 커밋에 도달한 가장 짧은 거리를 저장한다.
    #
    # 같은 커밋에 훨씬 긴 경로로 다시 도달하는 경우
    # 불필요한 탐색을 줄이는 데 사용한다.
    best_distance: dict[str, int] = {
        start_hash: 0,
    }

    # 큐가 빌 때까지 BFS를 계속한다.
    while queue:
        # 큐의 가장 앞 경로를 꺼낸다.
        current_path = queue.popleft()

        # 현재 경로의 마지막 커밋이 현재 위치이다.
        current_hash = current_path[-1]

        # 경로에 포함된 간선 수를 계산한다.
        #
        # 커밋 1개면 거리 0,
        # 커밋 2개면 거리 1이다.
        current_distance = len(current_path) - 1

        # 이미 최단 거리를 발견한 뒤,
        # 그보다 더 긴 경로는 최단 경로가 될 수 없으므로 탐색하지 않는다.
        if (
            shortest_distance is not None
            and current_distance > shortest_distance
        ):
            continue

        # 현재 위치가 목적지이면 최단 경로 후보로 저장한다.
        if current_hash == end_hash:
            shortest_distance = current_distance
            shortest_paths.append(current_path)

            # 목적지에서 다시 이웃으로 확장할 필요는 없다.
            continue

        # 현재 커밋에서 이동할 수 있는 부모와 자식 이웃을 가져온다.
        neighbors = _get_neighbors(
            commit_hash=current_hash,
            commits=commits,
            children=children,
        )

        # 모든 이웃 커밋을 확인한다.
        for neighbor_hash in neighbors:
            # PATH에서는 간선을 무방향으로 보기 때문에
            # A -> B -> A처럼 같은 커밋을 반복할 수 있다.
            #
            # 현재 경로에 이미 포함된 커밋이면 추가하지 않아
            # 경로 내부의 순환을 방지한다.
            if neighbor_hash in current_path:
                continue

            # 이웃으로 한 칸 이동하므로 거리를 1 증가시킨다.
            next_distance = current_distance + 1

            # 이전에 이 커밋에 도달한 최단 거리를 가져온다.
            previous_distance = best_distance.get(neighbor_hash)

            # 아직 방문하지 않았거나,
            # 기존 최단 거리와 같거나 더 짧은 경우에만 큐에 추가한다.
            #
            # 같은 거리를 허용하는 이유:
            # 동일한 길이의 최단 경로가 여러 개 존재할 수 있고,
            # 그중 사전순 최소 경로를 비교해야 하기 때문이다.
            if (
                previous_distance is None
                or next_distance <= previous_distance
            ):
                best_distance[neighbor_hash] = next_distance

                # 기존 경로에 이웃 hash를 추가한 새 경로를 큐에 넣는다.
                queue.append(current_path + [neighbor_hash])

    # 목적지에 도달한 경로가 하나도 없으면 연결되지 않은 그래프이다.
    if not shortest_paths:
        return None

    # 최단 경로가 여러 개이면 전체 경로 문자열을 비교하여
    # 사전순으로 가장 작은 경로를 반환한다.
    return _find_lexicographically_smallest_path(shortest_paths)


def _get_neighbors(
    commit_hash: str,
    commits: dict[str, Commit],
    children: dict[str, list[str]],
) -> list[str]:
    """
    Return the parent and child neighbours of one commit.
    """

    # 현재 커밋에서 이동 가능한 모든 이웃 hash를 저장한다.
    neighbors: list[str] = []

    # 현재 커밋 객체를 조회한다.
    commit = commits[commit_hash]

    # 자식 커밋에서 부모 커밋 방향으로 이동할 수 있도록
    # parents 목록을 이웃에 추가한다.
    for parent_hash in commit.parents:
        if parent_hash in commits:
            neighbors.append(parent_hash)

    # 부모 커밋에서 자식 커밋 방향으로도 이동할 수 있도록
    # children 인접 리스트의 값을 이웃에 추가한다.
    #
    # PATH 요구사항에서는 부모-자식 관계를 무방향 간선으로 보기 때문에
    # 부모와 자식 모두 이웃에 포함해야 한다.
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

    # 첫 번째 경로를 임시 최소 경로로 설정한다.
    smallest_path = paths[0]

    # 비교를 위해 경로를 hash1->hash2->... 형식의 문자열로 만든다.
    smallest_text = "->".join(smallest_path)

    # 나머지 경로를 하나씩 직접 비교한다.
    #
    # sorted()나 list.sort()는 과제에서 금지되어 있으므로 사용하지 않는다.
    for path in paths[1:]:
        path_text = "->".join(path)

        # Python 문자열 비교는 사전순으로 이루어진다.
        if path_text < smallest_text:
            smallest_path = path
            smallest_text = path_text

    return smallest_path