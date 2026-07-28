from __future__ import annotations

# hashlib는 커밋 hash를 생성하기 위해 사용한다.
#
# 이 프로젝트에서는 SHA-1을 사용하여
# 커밋 메시지, 작성자, 생성 시각, 카운터를 하나의 hash로 변환한다.
import hashlib

# datetime은 커밋 생성 시각을 저장하기 위해 사용한다.
from datetime import datetime

# 커밋 그래프 탐색 알고리즘을 가져온다.
#
# find_all_ancestors:
# 특정 커밋의 모든 조상을 DFS로 탐색한다.
#
# find_shortest_path:
# 두 커밋 사이의 최단 경로를 BFS로 탐색한다.
#
# topological_commit_order:
# 부모 커밋이 자식 커밋보다 먼저 나오도록 순서를 만든다.
from algorithms.graph import (
    find_all_ancestors,
    find_shortest_path,
    topological_commit_order,
)

# Python 표준 정렬 API 대신 직접 구현한 Merge Sort를 가져온다.
from algorithms.sorting import merge_sort

# 하나의 커밋 노드를 표현하는 Commit 클래스를 가져온다.
from models.commit import Commit


class MiniGit:
    """
    Mini Git 저장소의 상태를 관리하고 명령어 기능을 구현한다.

    이 클래스는 다음 정보를 메모리에 저장한다.

    - 전체 커밋
    - 브랜치와 각 브랜치의 HEAD
    - 현재 선택된 브랜치
    - 현재 사용자
    - 키워드 역색인
    - 작성자 역색인
    - 부모에서 자식으로 이동하기 위한 인접 리스트
    - commit hash 생성을 위한 카운터
    - 저장소 초기화 여부
    """

    def __init__(self) -> None:
        """
        빈 Mini Git 객체를 생성한다.

        INIT 명령이 실행되기 전까지 저장소는 초기화되지 않은 상태이다.
        """

        # commit hash -> Commit 객체
        #
        # hash를 key로 사용하기 때문에
        # 평균 O(1)에 특정 커밋을 빠르게 조회할 수 있다.
        self.commits: dict[str, Commit] = {}

        # branch name -> branch HEAD commit hash
        #
        # 브랜치는 전체 커밋 이력을 저장하지 않고,
        # 해당 브랜치의 최신 커밋 hash 하나만 가리킨다.
        #
        # 커밋이 없는 브랜치는 None을 가리킨다.
        self.branches: dict[str, str | None] = {}

        # 현재 선택된 브랜치 이름이다.
        #
        # 예:
        # "main"
        # "feature"
        self.current_branch: str | None = None

        # 새 커밋을 생성할 때 author로 사용되는 현재 사용자 이름이다.
        self.current_user: str | None = None

        # keyword -> commit hash 목록
        #
        # 커밋 메시지의 단어를 소문자로 정규화하여 저장한다.
        #
        # 예:
        # "login" -> ["abc123", "def456"]
        self.keyword_index: dict[str, list[str]] = {}

        # lower-case author name -> commit hash 목록
        #
        # 작성자 이름을 소문자로 정규화하여 검색 시 대소문자를 무시한다.
        #
        # 예:
        # "alice" -> ["abc123", "def456"]
        self.author_index: dict[str, list[str]] = {}

        # parent commit hash -> child commit hash 목록
        #
        # Commit 객체에는 부모 정보만 저장되어 있다.
        # PATH 기능에서는 부모-자식 관계를 무방향으로 탐색해야 하므로
        # 부모에서 자식 방향으로도 이동할 수 있도록 별도로 관리한다.
        self.children: dict[str, list[str]] = {}

        # commit hash 생성에 포함되는 증가 카운터이다.
        #
        # 같은 메시지, 작성자, timestamp가 입력되더라도
        # hash 생성 입력이 달라지도록 한다.
        self.commit_counter = 0

        # INIT 명령이 실행되었는지 나타낸다.
        #
        # False:
        # 저장소 초기화 전
        #
        # True:
        # 저장소 초기화 완료
        self.initialized = False

    def init_repository(self, user_name: str) -> str:
        """
        빈 저장소를 초기화한다.

        INIT 명령을 실행하면 다음 작업을 수행한다.

        - 기존 저장소 상태 초기화
        - main 브랜치 생성
        - 현재 브랜치를 main으로 설정
        - 현재 사용자 설정
        - 역색인 초기화
        - 자식 인접 리스트 초기화
        - commit counter 초기화

        Args:
            user_name:
                현재 사용자로 설정할 이름이다.

        Returns:
            저장소 초기화 결과 문자열을 반환한다.
        """

        # 사용자 이름 앞뒤의 불필요한 공백을 제거한다.
        user_name = user_name.strip()

        # 사용자 이름이 비어 있으면 잘못된 입력이다.
        if not user_name:
            return "Invalid args"

        # 기존 커밋 정보를 모두 초기화한다.
        self.commits = {}

        # main 브랜치를 생성한다.
        #
        # 아직 커밋이 없으므로 main HEAD는 None이다.
        self.branches = {
            "main": None,
        }

        # 현재 브랜치를 main으로 설정한다.
        self.current_branch = "main"

        # 입력받은 사용자 이름을 현재 작성자로 설정한다.
        self.current_user = user_name

        # 기존 역색인과 자식 인접 리스트를 모두 초기화한다.
        self.keyword_index = {}
        self.author_index = {}
        self.children = {}

        # hash 생성 카운터를 처음부터 다시 시작한다.
        self.commit_counter = 0

        # 저장소가 정상적으로 초기화되었음을 표시한다.
        self.initialized = True

        return (
            "Initialized repository.\n"
            "Current branch: main\n"
            f"Current user: {self.current_user}"
        )

    def create_branch(self, branch_name: str) -> str:
        """
        현재 브랜치의 HEAD를 가리키는 새 브랜치를 생성한다.

        BRANCH 명령은 새 브랜치를 만들지만,
        현재 브랜치를 자동으로 변경하지는 않는다.

        Args:
            branch_name:
                생성할 브랜치 이름이다.

        Returns:
            브랜치 생성 결과 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 브랜치 이름 앞뒤의 불필요한 공백을 제거한다.
        branch_name = branch_name.strip()

        # 빈 브랜치 이름은 허용하지 않는다.
        if not branch_name:
            return "Invalid args"

        # 같은 이름의 브랜치가 이미 존재하면 중복 생성하지 않는다.
        if branch_name in self.branches:
            return f"Branch already exists: {branch_name}"

        # 현재 브랜치가 가리키는 HEAD commit hash를 조회한다.
        current_head = self.branches[self.current_branch]

        # 새 브랜치도 생성 시점의 현재 HEAD를 가리키도록 한다.
        #
        # 예:
        # main -> abc123
        #
        # BRANCH feature 실행 후:
        # main -> abc123
        # feature -> abc123
        self.branches[branch_name] = current_head

        return f"Created branch: {branch_name}"

    def switch_branch(self, branch_name: str) -> str:
        """
        현재 브랜치를 기존 브랜치로 전환한다.

        Args:
            branch_name:
                이동할 브랜치 이름이다.

        Returns:
            브랜치 전환 결과 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 브랜치 이름 앞뒤의 공백을 제거한다.
        branch_name = branch_name.strip()

        # 빈 브랜치 이름은 허용하지 않는다.
        if not branch_name:
            return "Invalid args"

        # 존재하지 않는 브랜치로는 이동할 수 없다.
        if branch_name not in self.branches:
            return f"Unknown branch: {branch_name}"

        # 현재 선택된 브랜치 이름만 변경한다.
        #
        # 커밋 객체나 브랜치 이력을 복사하는 것이 아니다.
        self.current_branch = branch_name

        return f"Switched to branch: {branch_name}"

    def create_commit(self, message: str) -> str:
        """
        현재 브랜치에 새 커밋을 생성한다.

        이전 브랜치 HEAD가 새 커밋의 부모가 되고,
        새 커밋 생성 후 현재 브랜치 HEAD가 새 커밋으로 이동한다.

        커밋 생성 시 다음 자료구조도 함께 갱신한다.

        - commits
        - branches
        - children
        - keyword_index
        - author_index

        Args:
            message:
                사용자가 입력한 커밋 메시지이다.

        Returns:
            새 커밋 정보 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 메시지 앞뒤의 불필요한 공백을 제거한다.
        message = message.strip()

        # 빈 커밋 메시지는 허용하지 않는다.
        if not message:
            return "Invalid args"

        # 현재 시간을 커밋 생성 시각으로 저장한다.
        timestamp = datetime.now()

        # 현재 브랜치가 가리키는 HEAD commit hash를 조회한다.
        current_head = self.branches[self.current_branch]

        # 부모 commit hash를 저장할 리스트이다.
        parents: list[str] = []

        # 첫 번째 커밋이 아니면 현재 HEAD를 부모로 설정한다.
        #
        # 첫 번째 커밋:
        # parents = []
        #
        # 일반 커밋:
        # parents = ["previous_hash"]
        if current_head is not None:
            parents.append(current_head)

        # 세션 내에서 중복되지 않는 commit hash를 생성한다.
        commit_hash = self._generate_commit_hash(
            message=message,
            author=self.current_user,
            timestamp=timestamp,
        )

        # 새 Commit 객체를 생성한다.
        commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.current_user,
            timestamp=timestamp,
            parents=parents,
        )

        # commit hash를 key로 사용하여 새 커밋을 저장한다.
        #
        # 이후 hash로 평균 O(1)에 조회할 수 있다.
        self.commits[commit_hash] = commit

        # 현재 브랜치 HEAD를 새 커밋으로 이동한다.
        self.branches[self.current_branch] = commit_hash

        # 새 커밋도 추후 다른 커밋의 부모가 될 수 있으므로
        # 빈 자식 목록을 미리 준비한다.
        if commit_hash not in self.children:
            self.children[commit_hash] = []

        # 각 부모 커밋의 children 목록에
        # 새 커밋 hash를 추가한다.
        #
        # 필수 기능에서는 부모가 보통 하나지만,
        # parents가 리스트이므로 여러 부모도 처리할 수 있다.
        for parent_hash in parents:
            if parent_hash not in self.children:
                self.children[parent_hash] = []

            self.children[parent_hash].append(commit_hash)

        # 커밋 메시지 키워드와 작성자 역색인을 갱신한다.
        #
        # 검색 시점이 아니라 COMMIT 시점에 미리 인덱스를 만든다.
        self._update_indexes(commit)

        return (
            f"[{self.current_branch} {commit.hash}] "
            f"{commit.message}"
        )

    def show_log(self) -> str:
        """
        모든 커밋을 부모 우선 순서로 출력한다.

        일반 Git처럼 최신순으로 출력하지 않고,
        부모 커밋이 항상 자식 커밋보다 먼저 나오도록 한다.

        Returns:
            포맷팅된 로그 문자열 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 생성된 커밋이 하나도 없으면 로그가 없다.
        if not self.commits:
            return "No commits"

        # DFS 기반 부모 우선 순서를 계산한다.
        ordered_hashes = topological_commit_order(self.commits)

        # 각 커밋의 출력 문자열을 저장한다.
        output: list[str] = []

        # 계산된 순서에 따라 commit hash를 하나씩 확인한다.
        for commit_hash in ordered_hashes:
            # hash를 이용해 Commit 객체를 조회한다.
            commit = self.commits[commit_hash]

            # 사람이 읽을 수 있는 형식으로 변환하여 결과에 추가한다.
            output.append(self._format_commit(commit))

        # 커밋 사이를 빈 줄로 구분한다.
        return "\n\n".join(output)

    def show_sorted_log(self, sort_by: str) -> str:
        """
        커밋을 날짜 또는 작성자 기준으로 정렬하여 출력한다.

        Python 표준 정렬 API를 사용하지 않고
        직접 구현한 Merge Sort를 사용한다.

        Args:
            sort_by:
                정렬 기준이다.

                허용 값:
                - date
                - author

        Returns:
            정렬된 로그 문자열 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 커밋이 하나도 없으면 정렬할 데이터가 없다.
        if not self.commits:
            return "No commits"

        # commits 딕셔너리의 Commit 객체들을 리스트로 변환한다.
        commits = list(self.commits.values())

        # 날짜 기준 정렬이다.
        if sort_by == "date":
            # Merge Sort에 timestamp 비교 함수를 전달한다.
            ordered_commits = merge_sort(
                commits,
                self._date_before_or_equal,
            )

        # 작성자 기준 정렬이다.
        elif sort_by == "author":
            # Merge Sort에 author 비교 함수를 전달한다.
            ordered_commits = merge_sort(
                commits,
                self._author_before_or_equal,
            )

        # date와 author 이외의 기준은 허용하지 않는다.
        else:
            return "Invalid args"

        # 정렬 결과를 출력 문자열로 변환한다.
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
        두 커밋 사이의 최단 경로를 출력한다.

        부모-자식 연결은 무방향 간선으로 간주한다.

        Args:
            start_hash:
                시작 커밋 hash이다.

            end_hash:
                도착 커밋 hash이다.

        Returns:
            최단 경로, No path 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 시작 커밋이 존재하는지 확인한다.
        if start_hash not in self.commits:
            return f"Unknown commit: {start_hash}"

        # 도착 커밋이 존재하는지 확인한다.
        if end_hash not in self.commits:
            return f"Unknown commit: {end_hash}"

        # BFS 기반 최단 경로 탐색 함수를 호출한다.
        path = find_shortest_path(
            start_hash=start_hash,
            end_hash=end_hash,
            commits=self.commits,
            children=self.children,
        )

        # 두 커밋이 연결되지 않은 경우이다.
        if path is None:
            return "No path"

        # hash 목록을 화살표 형식의 문자열로 변환한다.
        #
        # 예:
        # ["aaa111", "bbb222", "ccc333"]
        #
        # 결과:
        # aaa111 -> bbb222 -> ccc333
        return f"Path: {' -> '.join(path)}"

    def show_ancestors(self, commit_hash: str) -> str:
        """
        특정 커밋에서 도달 가능한 모든 조상을 출력한다.

        대상 커밋 자신은 조상 목록에 포함하지 않는다.

        Args:
            commit_hash:
                조상을 탐색할 기준 커밋 hash이다.

        Returns:
            조상 목록 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 대상 커밋이 존재하는지 확인한다.
        if commit_hash not in self.commits:
            return f"Unknown commit: {commit_hash}"

        # 부모 방향 DFS로 모든 조상 hash를 가져온다.
        ancestor_hashes = find_all_ancestors(
            commit_hash=commit_hash,
            commits=self.commits,
        )

        # 첫 번째 커밋처럼 부모가 없는 경우이다.
        if not ancestor_hashes:
            return "No ancestors"

        # 각 조상을 출력 형식으로 변환한다.
        output: list[str] = []

        for ancestor_hash in ancestor_hashes:
            ancestor = self.commits[ancestor_hash]
            output.append(self._format_commit(ancestor))

        return "\n\n".join(output)

    def search_keyword(self, keyword: str) -> str:
        """
        키워드 역색인을 이용하여 커밋 메시지를 검색한다.

        여러 단어 검색도 지원한다.

        예:
            SEARCH "login feature"

        이 경우 login과 feature 토큰을 모두 포함한 커밋을 반환한다.

        Args:
            keyword:
                검색할 키워드 또는 여러 키워드 문자열이다.

        Returns:
            검색 결과 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 검색어를 소문자로 변환하고 공백 기준으로 나눈다.
        #
        # 예:
        # "Login Feature"
        #
        # 결과:
        # ["login", "feature"]
        query_tokens = keyword.strip().lower().split()

        # 검색어가 비어 있으면 잘못된 입력이다.
        if not query_tokens:
            return "Invalid args"

        # 첫 번째 검색 토큰을 기준 후보로 사용한다.
        first_token = query_tokens[0]

        # 첫 번째 토큰이 인덱스에 없으면 결과가 없다.
        if first_token not in self.keyword_index:
            return "Found 0 commits"

        # 첫 번째 토큰에 해당하는 commit hash 목록을 복사한다.
        #
        # 원본 인덱스 목록을 직접 수정하지 않기 위해 [:]를 사용한다.
        candidate_hashes = self.keyword_index[first_token][:]

        # 검색어가 여러 토큰이면 나머지 토큰과 교집합을 구한다.
        for token in query_tokens[1:]:
            # 현재 토큰에 해당하는 hash 목록을 가져온다.
            matching_hashes = self.keyword_index.get(token)

            # 하나의 토큰이라도 인덱스에 없으면
            # 모든 토큰을 포함하는 커밋은 존재하지 않는다.
            if matching_hashes is None:
                return "Found 0 commits"

            # membership 검사를 빠르게 하기 위해 set으로 변환한다.
            matching_set = set(matching_hashes)

            # 현재 토큰까지 모두 일치하는 후보만 저장한다.
            filtered_candidates: list[str] = []

            for commit_hash in candidate_hashes:
                if commit_hash in matching_set:
                    filtered_candidates.append(commit_hash)

            # 필터링된 목록을 다음 반복의 후보로 사용한다.
            candidate_hashes = filtered_candidates

            # 후보가 모두 제거되면 더 확인할 필요가 없다.
            if not candidate_hashes:
                return "Found 0 commits"

        # 최종 후보 목록을 검색 결과 형식으로 출력한다.
        return self._format_search_results(candidate_hashes)

    def search_author(self, author: str) -> str:
        """
        작성자 역색인을 이용하여 커밋을 검색한다.

        작성자 이름은 대소문자를 구분하지 않는다.

        Args:
            author:
                검색할 작성자 이름이다.

        Returns:
            검색 결과 또는 에러 메시지를 반환한다.
        """

        # INIT이 실행되지 않은 경우 에러를 반환한다.
        repository_error = self._get_repository_error()

        if repository_error:
            return repository_error

        # 작성자 이름의 앞뒤 공백을 제거하고 소문자로 정규화한다.
        author_key = author.strip().lower()

        # 빈 작성자 이름은 허용하지 않는다.
        if not author_key:
            return "Invalid args"

        # 작성자 인덱스에서 해당 commit hash 목록을 가져온다.
        commit_hashes = self.author_index.get(author_key, [])

        # 검색 결과가 없으면 0개를 반환한다.
        if not commit_hashes:
            return "Found 0 commits"

        return self._format_search_results(commit_hashes)

    def _get_repository_error(self) -> str | None:
        """
        저장소 초기화 여부를 확인한다.

        Returns:
            INIT이 실행되지 않았다면 에러 문자열을 반환한다.
            초기화가 완료되었다면 None을 반환한다.
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
        세션 내에서 중복되지 않는 6자리 commit hash를 생성한다.

        hash 입력에는 다음 정보가 포함된다.

        - 증가 카운터
        - 커밋 메시지
        - 작성자
        - timestamp

        생성된 hash가 기존 commits 딕셔너리에 이미 존재하면
        카운터를 증가시켜 다시 생성한다.

        Args:
            message:
                커밋 메시지이다.

            author:
                커밋 작성자이다.

            timestamp:
                커밋 생성 시각이다.

        Returns:
            중복되지 않는 6자리 hash 문자열을 반환한다.
        """

        # 중복되지 않는 hash가 생성될 때까지 반복한다.
        while True:
            # 매 시도마다 카운터를 증가시킨다.
            self.commit_counter += 1

            # hash 입력으로 사용할 문자열을 만든다.
            #
            # 구분자 "|"를 사용하여 각 값을 명확히 구분한다.
            source_text = (
                f"{self.commit_counter}|"
                f"{message}|"
                f"{author}|"
                f"{timestamp.isoformat()}"
            )

            # 문자열을 UTF-8 bytes로 변환한 뒤 SHA-1 hash를 생성한다.
            full_hash = hashlib.sha1(
                source_text.encode("utf-8")
            ).hexdigest()

            # 터미널 출력 가독성을 위해 앞 6자리만 사용한다.
            commit_hash = full_hash[:6]

            # 기존 커밋과 중복되지 않으면 반환한다.
            #
            # 충돌이 발생하면 while문이 다시 실행된다.
            if commit_hash not in self.commits:
                return commit_hash

    def _update_indexes(self, commit: Commit) -> None:
        """
        새 커밋을 작성자 및 키워드 역색인에 추가한다.

        인덱스는 검색할 때 생성하지 않고
        COMMIT 생성 시점에 미리 갱신한다.

        Args:
            commit:
                새로 생성된 Commit 객체이다.
        """

        # 작성자 이름을 소문자로 정규화한다.
        author_key = commit.author.lower()

        # 해당 작성자 key가 처음 등장하면 빈 목록을 만든다.
        if author_key not in self.author_index:
            self.author_index[author_key] = []

        # 작성자 인덱스에 새 커밋 hash를 추가한다.
        self.author_index[author_key].append(commit.hash)

        # 커밋 메시지를 소문자로 변환하고 공백 기준으로 분리한다.
        #
        # 예:
        # "Add Login Feature"
        #
        # 결과:
        # ["add", "login", "feature"]
        message_tokens = commit.message.lower().split()

        # 한 메시지 안에서 같은 단어가 반복될 수 있다.
        #
        # 예:
        # "login login login"
        #
        # 같은 commit hash가 인덱스에 여러 번 들어가지 않도록
        # 이미 추가한 토큰을 set으로 관리한다.
        added_tokens: set[str] = set()

        for token in message_tokens:
            # 현재 커밋에서 이미 처리한 토큰이면 건너뛴다.
            if token in added_tokens:
                continue

            # 토큰이 처음 등장하면 빈 hash 목록을 만든다.
            if token not in self.keyword_index:
                self.keyword_index[token] = []

            # 토큰에 해당하는 커밋 hash를 저장한다.
            self.keyword_index[token].append(commit.hash)

            # 현재 토큰을 처리 완료 상태로 기록한다.
            added_tokens.add(token)

    def _branch_labels(self, commit_hash: str) -> list[str]:
        """
        특정 커밋을 현재 HEAD로 가리키는 브랜치 이름을 반환한다.

        Args:
            commit_hash:
                브랜치 라벨을 확인할 커밋 hash이다.

        Returns:
            해당 커밋을 가리키는 브랜치 이름 목록을 반환한다.
        """

        # 일치하는 브랜치 이름을 저장한다.
        labels: list[str] = []

        # 모든 브랜치와 각 브랜치 HEAD를 확인한다.
        for branch_name, branch_head in self.branches.items():
            # 브랜치 HEAD가 현재 커밋과 같으면 라벨 목록에 추가한다.
            if branch_head == commit_hash:
                labels.append(branch_name)

        return labels

    def _format_commit(self, commit: Commit) -> str:
        """
        Commit 객체를 사람이 읽기 쉬운 로그 문자열로 변환한다.

        Args:
            commit:
                출력할 Commit 객체이다.

        Returns:
            hash, author, timestamp, branch label, message가 포함된
            문자열을 반환한다.
        """

        # datetime 객체를 정해진 날짜 형식의 문자열로 변환한다.
        timestamp_text = commit.timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # 현재 커밋을 가리키는 브랜치 이름을 가져온다.
        branch_labels = self._branch_labels(commit.hash)

        # 기본적으로 브랜치 라벨은 빈 문자열이다.
        branch_text = ""

        # 하나 이상의 브랜치가 현재 커밋을 가리키면
        # [main, feature] 형식으로 표시한다.
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
        키워드 또는 작성자 검색 결과를 일정한 형식으로 변환한다.

        Args:
            commit_hashes:
                검색 결과에 포함된 commit hash 목록이다.

        Returns:
            검색 결과 개수와 커밋 정보를 포함한 문자열을 반환한다.
        """

        # 첫 줄에 검색 결과 개수를 표시한다.
        output = [
            f"Found {len(commit_hashes)} commit(s):",
        ]

        # 각 hash에 해당하는 Commit 객체를 조회한다.
        for commit_hash in commit_hashes:
            commit = self.commits[commit_hash]

            # hash, 메시지, 작성자를 한 줄로 표시한다.
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
        두 커밋을 timestamp 기준으로 비교한다.

        timestamp가 같으면 hash를 동률 처리 기준으로 사용한다.

        Args:
            first:
                첫 번째 Commit 객체이다.

            second:
                두 번째 Commit 객체이다.

        Returns:
            first가 second보다 앞에 오거나 같아야 하면 True를 반환한다.
        """

        # timestamp가 같으면 hash 문자열을 비교하여
        # 항상 일관된 정렬 결과를 만든다.
        if first.timestamp == second.timestamp:
            return first.hash <= second.hash

        # 더 이른 timestamp를 가진 커밋이 먼저 온다.
        return first.timestamp < second.timestamp

    @staticmethod
    def _author_before_or_equal(
        first: Commit,
        second: Commit,
    ) -> bool:
        """
        두 커밋을 작성자 이름 기준으로 비교한다.

        비교 우선순위:

        1. 작성자 이름
        2. timestamp
        3. hash

        Args:
            first:
                첫 번째 Commit 객체이다.

            second:
                두 번째 Commit 객체이다.

        Returns:
            first가 second보다 앞에 오거나 같아야 하면 True를 반환한다.
        """

        # 작성자 비교 시 대소문자를 무시하기 위해 소문자로 변환한다.
        first_author = first.author.lower()
        second_author = second.author.lower()

        # 작성자가 다르면 이름의 사전순으로 비교한다.
        if first_author != second_author:
            return first_author < second_author

        # 작성자가 같으면 timestamp를 비교한다.
        if first.timestamp != second.timestamp:
            return first.timestamp < second.timestamp

        # 작성자와 timestamp가 모두 같으면
        # hash를 마지막 동률 처리 기준으로 사용한다.
        return first.hash <= second.hash