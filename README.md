# B3-2 Mini Git 구축

Python으로 구현한 CLI 기반 Mini Git 프로그램입니다.

실제 Git의 모든 기능을 재현하는 대신, 커밋 메타데이터를 중심으로 Git의 핵심 구조인 커밋 그래프, 브랜치, HEAD, 그래프 탐색, 정렬 알고리즘, 역색인을 직접 구현하였습니다.

이 프로젝트에서 다루는 핵심 흐름은 다음과 같습니다.

```text
사용자 명령 입력
    ↓
CLI 명령어 파싱
    ↓
MiniGit 저장소 기능 실행
    ↓
커밋 그래프 및 브랜치 상태 변경
    ↓
그래프 탐색 / 정렬 / 역색인 검색
    ↓
결과 출력
```

---

## 1. 프로젝트 목표

Git의 커밋은 단순한 최신순 목록이 아니라, 각 커밋이 부모 커밋을 가리키는 그래프 구조로 연결되어 있습니다.

본 프로젝트에서는 다음 내용을 직접 구현하고 설명할 수 있도록 하는 것을 목표로 하였습니다.

- 커밋 그래프와 DAG 구조
- 브랜치와 HEAD의 동작 원리
- 부모 커밋 우선 로그 출력
- BFS 기반 최단 경로 탐색
- DFS 기반 모든 조상 탐색
- 직접 구현한 Merge Sort
- 역색인 기반 키워드 및 작성자 검색
- 알고리즘별 시간복잡도
- CLI 기반 REPL 인터페이스
- 잘못된 입력에 대한 일관된 에러 처리

---

## 2. 구현 범위

### 구현한 기능

- `INIT <user_name>`
- `BRANCH <branch_name>`
- `SWITCH <branch_name>`
- `COMMIT <message>`
- `LOG`
- `LOG --sort-by=date`
- `LOG --sort-by=author`
- `PATH <commit1> <commit2>`
- `ANCESTORS <commit_hash>`
- `SEARCH <keyword>`
- `SEARCH --author=<name>`
- `exit`
- `quit`

### 구현하지 않은 기능

본 프로젝트에서는 필수 기능 구현과 핵심 알고리즘 학습에 집중하였으며, 다음 보너스 기능은 구현하지 않았습니다.

- Diff
- Merge 명령
- 두 개 이상의 정렬 알고리즘 성능 비교
- 실제 파일 내용 추적
- staging area
- 네트워크 통신
- 데이터 영속성
- push / pull / fetch
- rebase
- cherry-pick

프로그램은 메모리에서만 동작합니다.

프로그램을 종료하면 생성한 커밋, 브랜치, 인덱스 정보는 모두 사라집니다.

---

## 3. 개발 환경

- Python 3.10 이상
- CLI 기반 프로그램
- 외부 패키지 사용 없음
- 그래프 전용 라이브러리 사용 없음
- Python 표준 정렬 API 사용 없음
  - `sorted()` 사용 금지
  - `list.sort()` 사용 금지
- 기본 자료형 사용
  - `list`
  - `dict`
  - `set`
- 표준 라이브러리 사용
  - `datetime`
  - `hashlib`
  - `shlex`
  - `collections.deque`
  - `dataclasses`

---

## 4. 실행 방법

프로젝트 루트 디렉터리에서 실행합니다.

```bash
python3 main.py
```

가상 환경을 사용하는 경우:

```bash
source .venv/bin/activate
python main.py
```

실행 후 다음 화면이 나타납니다.

```text
Mini Git
Enter 'exit' or 'quit' to close the program.
mini-git>
```

종료 명령어:

```text
exit
```

또는:

```text
quit
```

---

## 5. 프로젝트 구조

```text
B3-2/
├── README.md
├── main.py
├── mini_git.py
├── models/
│   ├── __init__.py
│   └── commit.py
├── algorithms/
│   ├── __init__.py
│   ├── graph.py
│   └── sorting.py
└── tests/
    ├── basic_commands.txt
    ├── branch_commands.txt
    ├── search_commands.txt
    └── error_commands.txt
```

---

## 6. 파일별 역할

### 6.1 `main.py`

CLI 인터페이스와 명령어 파싱을 담당합니다.

주요 역할:

- `MiniGit` 객체 생성
- `mini-git>` 프롬프트 출력
- 사용자 명령 반복 입력
- `shlex.split()`을 이용한 따옴표 처리
- 명령어 대소문자 정규화
- 명령어별 인자 개수 확인
- 명령어에 맞는 메서드 호출
- `exit`, `quit`, EOF, `Ctrl+C` 처리
- 결과 출력

핵심 흐름:

```python
repository = MiniGit()

while True:
    raw_command = input("mini-git> ").strip()
    parts = shlex.split(raw_command)

    command = parts[0].lower()
    args = parts[1:]

    result = execute_command(
        repository=repository,
        command=command,
        args=args,
    )

    print(result)
```

`MiniGit` 객체는 반복문 밖에서 한 번만 생성됩니다.

```python
repository = MiniGit()
```

따라서 한 실행 세션 동안 생성한 커밋과 브랜치 정보가 계속 유지됩니다.

---

### 6.2 `mini_git.py`

저장소 상태와 Mini Git의 명령어 기능을 담당합니다.

주요 역할:

- 저장소 초기화
- 브랜치 생성
- 브랜치 전환
- 커밋 생성
- commit hash 생성
- 브랜치 HEAD 갱신
- 부모-자식 관계 저장
- 역색인 갱신
- 로그 출력
- 날짜 및 작성자 정렬
- 최단 경로 탐색 요청
- 조상 탐색 요청
- 키워드 및 작성자 검색
- 출력 형식 생성
- 에러 처리

---

### 6.3 `models/commit.py`

하나의 커밋 노드를 표현하는 `Commit` 클래스를 정의합니다.

```python
@dataclass
class Commit:
    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: list[str]
```

| 필드 | 역할 |
|---|---|
| `hash` | 커밋의 고유 식별자 |
| `message` | 커밋 메시지 |
| `author` | 커밋 작성자 |
| `timestamp` | 커밋 생성 시각 |
| `parents` | 부모 커밋 hash 목록 |

`parents`는 하나의 문자열이 아니라 리스트로 구현하였습니다.

```python
parents: list[str]
```

현재 필수 기능에서는 일반 커밋이 부모를 0개 또는 1개 가지지만, 자료구조 자체는 여러 부모를 저장할 수 있습니다.

따라서 추후 merge commit처럼 부모가 2개인 구조로 확장할 수 있습니다.

---

### 6.4 `algorithms/graph.py`

그래프 탐색 관련 알고리즘을 담당합니다.

주요 함수:

| 함수 | 역할 |
|---|---|
| `topological_commit_order()` | 부모 커밋 우선 로그 순서 생성 |
| `_visit_commit_for_log()` | DFS로 부모를 먼저 방문 |
| `find_shortest_path()` | BFS로 두 커밋 사이의 최단 경로 탐색 |
| `_get_neighbors()` | 부모와 자식 이웃 조회 |
| `_find_lexicographically_smallest_path()` | 여러 최단 경로 중 사전순 최소 경로 선택 |
| `find_all_ancestors()` | 특정 커밋의 모든 조상 탐색 |
| `_visit_ancestor()` | 부모 방향 DFS 탐색 |

그래프 탐색 로직을 `mini_git.py`와 분리하여 저장소 관리와 알고리즘 구현이 섞이지 않도록 구성하였습니다.

---

### 6.5 `algorithms/sorting.py`

Python의 표준 정렬 API를 사용하지 않고 직접 구현한 Merge Sort가 포함되어 있습니다.

주요 함수:

| 함수 | 역할 |
|---|---|
| `merge_sort()` | 리스트를 분할하고 재귀적으로 정렬 |
| `_merge()` | 두 정렬된 리스트를 하나로 병합 |

비교 함수를 매개변수로 전달하기 때문에 동일한 Merge Sort를 날짜 정렬과 작성자 정렬에 모두 사용할 수 있습니다.

---

## 7. 핵심 자료구조

`MiniGit` 클래스는 다음 상태를 관리합니다.

```text
MiniGit
├── commits
├── branches
├── current_branch
├── current_user
├── keyword_index
├── author_index
├── children
├── commit_counter
└── initialized
```

| 변수 | 타입 | 책임 |
|---|---|---|
| `commits` | `dict[str, Commit]` | hash로 커밋 객체 조회 |
| `branches` | `dict[str, str \| None]` | 브랜치 이름과 HEAD hash 연결 |
| `current_branch` | `str \| None` | 현재 선택된 브랜치 |
| `current_user` | `str \| None` | 새 커밋의 작성자 |
| `keyword_index` | `dict[str, list[str]]` | 키워드별 커밋 hash 목록 |
| `author_index` | `dict[str, list[str]]` | 작성자별 커밋 hash 목록 |
| `children` | `dict[str, list[str]]` | 부모 hash별 자식 hash 목록 |
| `commit_counter` | `int` | hash 생성 입력의 고유성 강화 |
| `initialized` | `bool` | INIT 실행 여부 |

---

## 8. 전체 데이터 구조

```text
MiniGit
│
├── commits
│   └── commit_hash -> Commit
│                         ├── hash
│                         ├── message
│                         ├── author
│                         ├── timestamp
│                         └── parents
│
├── branches
│   └── branch_name -> HEAD commit_hash
│
├── current_branch
│   └── 현재 선택된 브랜치 이름
│
├── current_user
│   └── 새 커밋의 작성자
│
├── children
│   └── parent_hash -> child_hash 목록
│
├── keyword_index
│   └── keyword -> commit_hash 목록
│
└── author_index
    └── author -> commit_hash 목록
```

---

## 9. CLI 명령어 문법

### 9.1 명령어 대소문자

명령어는 대소문자를 구분하지 않습니다.

```python
command = parts[0].lower()
```

따라서 다음 명령은 모두 동일하게 처리됩니다.

```text
INIT "Alice"
init "Alice"
Init "Alice"
```

---

### 9.2 공백이 포함된 문자열

사용자 이름, 커밋 메시지, 검색 키워드에 공백이 포함되면 따옴표로 감쌉니다.

```text
INIT "Alice Kim"
COMMIT "Add login feature"
SEARCH "login feature"
```

일반적인 `.split()`이 아니라 `shlex.split()`을 사용합니다.

```python
parts = shlex.split(raw_command)
```

입력:

```text
COMMIT "Add login feature"
```

파싱 결과:

```python
[
    "COMMIT",
    "Add login feature"
]
```

작성자 이름에 공백이 포함된 경우 전체 옵션을 따옴표로 감쌉니다.

```text
SEARCH "--author=Alice Kim"
```

---

### 9.3 옵션 형식

```text
SEARCH --author=<name>
LOG --sort-by=date
LOG --sort-by=author
```

예:

```text
SEARCH --author=Alice
```

공백이 있는 작성자:

```text
SEARCH "--author=Alice Kim"
```

---

### 9.4 잘못된 따옴표

닫히지 않은 따옴표가 입력되면 `shlex.split()`에서 `ValueError`가 발생할 수 있습니다.

```python
try:
    parts = shlex.split(raw_command)
except ValueError:
    print("Invalid args")
    continue
```

입력:

```text
COMMIT "Add login feature
```

출력:

```text
Invalid args
```

프로그램은 종료되지 않고 다음 명령을 계속 입력받습니다.

---

## 10. 명령어 목록

| 명령어 | 설명 |
|---|---|
| `INIT <user_name>` | 저장소를 초기화하고 main 브랜치를 생성 |
| `BRANCH <branch_name>` | 현재 HEAD를 가리키는 새 브랜치 생성 |
| `SWITCH <branch_name>` | 지정한 브랜치로 전환 |
| `COMMIT <message>` | 현재 브랜치에 새 커밋 생성 |
| `LOG` | 부모 커밋 우선 순서로 로그 출력 |
| `LOG --sort-by=date` | timestamp 기준 로그 정렬 |
| `LOG --sort-by=author` | 작성자 이름 기준 로그 정렬 |
| `PATH <commit1> <commit2>` | 두 커밋 사이 최단 경로 출력 |
| `ANCESTORS <commit_hash>` | 특정 커밋의 모든 조상 출력 |
| `SEARCH <keyword>` | 메시지 키워드로 커밋 검색 |
| `SEARCH --author=<name>` | 작성자로 커밋 검색 |
| `exit` | 프로그램 종료 |
| `quit` | 프로그램 종료 |

---

## 11. INIT

명령어:

```text
INIT "Alice"
```

처리 순서:

```text
사용자 이름 확인
    ↓
기존 저장소 상태 초기화
    ↓
main 브랜치 생성
    ↓
main HEAD = None
    ↓
current_branch = main
    ↓
current_user = Alice
    ↓
역색인과 자식 인접 리스트 초기화
    ↓
initialized = True
```

초기 상태:

```python
self.branches = {
    "main": None,
}

self.current_branch = "main"
self.current_user = "Alice"
```

아직 커밋이 없기 때문에 `main` 브랜치는 `None`을 가리킵니다.

출력:

```text
Initialized repository.
Current branch: main
Current user: Alice
```

---

## 12. 브랜치와 HEAD

브랜치는 전체 커밋 이력을 복사하지 않습니다.

각 브랜치는 해당 브랜치의 최신 커밋 hash 하나만 가리킵니다.

```python
self.branches = {
    "main": "abc123",
    "feature": "def456",
}
```

현재 브랜치는 별도로 저장합니다.

```python
self.current_branch = "main"
```

현재 HEAD는 다음 방식으로 확인할 수 있습니다.

```python
current_head = self.branches[self.current_branch]
```

즉 이 프로젝트에서 HEAD의 의미는 다음 두 단계로 표현됩니다.

```text
current_branch
    ↓
branches[current_branch]
    ↓
현재 HEAD commit hash
```

---

## 13. BRANCH

명령어:

```text
BRANCH feature
```

새 브랜치는 생성 시점의 현재 HEAD를 가리킵니다.

생성 전:

```python
branches = {
    "main": "aaa111",
}
```

생성 후:

```python
branches = {
    "main": "aaa111",
    "feature": "aaa111",
}
```

`BRANCH`는 새 브랜치를 생성할 뿐, 현재 브랜치를 자동으로 변경하지 않습니다.

```python
self.current_branch == "main"
```

새 브랜치로 이동하려면 별도로 다음 명령을 사용해야 합니다.

```text
SWITCH feature
```

---

## 14. SWITCH

명령어:

```text
SWITCH feature
```

처리:

```python
self.current_branch = "feature"
```

브랜치의 커밋 목록을 복사하거나 커밋 객체를 이동하는 것이 아닙니다.

현재 어떤 브랜치에서 작업할지만 변경합니다.

존재하지 않는 브랜치를 입력하면 다음을 출력합니다.

```text
Unknown branch: unknown
```

---

## 15. COMMIT

명령어:

```text
COMMIT "Add login feature"
```

처리 순서:

```text
저장소 초기화 여부 확인
    ↓
커밋 메시지 확인
    ↓
현재 timestamp 생성
    ↓
현재 브랜치 HEAD 조회
    ↓
부모 hash 목록 생성
    ↓
고유 commit hash 생성
    ↓
Commit 객체 생성
    ↓
commits 딕셔너리에 저장
    ↓
현재 브랜치 HEAD 갱신
    ↓
children 인접 리스트 갱신
    ↓
keyword_index 갱신
    ↓
author_index 갱신
    ↓
결과 출력
```

현재 HEAD 확인:

```python
current_head = self.branches[self.current_branch]
```

부모 목록 생성:

```python
parents: list[str] = []

if current_head is not None:
    parents.append(current_head)
```

첫 번째 커밋:

```python
parents = []
```

두 번째 커밋 이후:

```python
parents = ["previous_commit_hash"]
```

커밋 저장:

```python
self.commits[commit_hash] = commit
```

현재 브랜치 HEAD 이동:

```python
self.branches[self.current_branch] = commit_hash
```

---

## 16. 브랜치 분기 예시

명령:

```text
INIT "Alice"
COMMIT "Initial commit"
BRANCH feature
COMMIT "Main work"
SWITCH feature
COMMIT "Feature work"
```

그래프:

```text
                         Main work
                        /
Initial commit
                        \
                         Feature work
```

브랜치 상태:

```python
branches = {
    "main": "main_work_hash",
    "feature": "feature_work_hash",
}
```

`main`에서 새 커밋을 생성해도 `feature` HEAD는 자동으로 이동하지 않습니다.

각 브랜치는 독립적으로 자신의 최신 커밋을 가리킵니다.

---

## 17. commit hash 생성

commit hash는 다음 정보를 결합하여 생성합니다.

```text
commit_counter
message
author
timestamp
```

코드 구조:

```python
source_text = (
    f"{self.commit_counter}|"
    f"{message}|"
    f"{author}|"
    f"{timestamp.isoformat()}"
)
```

SHA-1을 적용합니다.

```python
full_hash = hashlib.sha1(
    source_text.encode("utf-8")
).hexdigest()
```

출력 가독성을 위해 앞 6자리만 사용합니다.

```python
commit_hash = full_hash[:6]
```

예:

```text
254a69
```

---

## 18. hash 중복과 충돌 방지

6자리 hash는 전체 SHA-1보다 표현 가능한 경우의 수가 적기 때문에 이론적으로 충돌 가능성이 있습니다.

따라서 생성한 hash가 이미 존재하는지 반드시 확인합니다.

```python
if commit_hash not in self.commits:
    return commit_hash
```

중복이면 반복문을 다시 실행합니다.

```python
while True:
    self.commit_counter += 1
```

카운터가 변경되므로 새로운 입력값으로 hash가 다시 생성됩니다.

따라서 세션 내부에서는 중복 hash를 저장하지 않습니다.

---

## 19. 커밋 저장소와 빠른 조회

모든 커밋은 다음 딕셔너리에 저장합니다.

```python
self.commits: dict[str, Commit] = {}
```

구조:

```text
commit hash -> Commit 객체
```

예:

```python
commits = {
    "aaa111": Commit(...),
    "bbb222": Commit(...),
    "ccc333": Commit(...),
}
```

조회:

```python
commit = self.commits[commit_hash]
```

Python 딕셔너리의 평균 조회 시간은 다음과 같습니다.

```text
O(1)
```

커밋을 리스트에만 저장하면 특정 hash를 찾기 위해 모든 커밋을 확인해야 합니다.

```text
O(n)
```

따라서 commit hash를 key로 사용하는 딕셔너리가 빠른 커밋 조회에 적합합니다.

---

## 20. 커밋 그래프가 DAG인 이유

DAG는 Directed Acyclic Graph, 즉 방향성 비순환 그래프입니다.

### Directed

각 커밋은 자신의 부모 커밋을 가리킵니다.

```text
새 커밋 -> 이전 커밋
```

따라서 간선에 방향이 존재합니다.

### Acyclic

새 커밋은 이미 존재하는 과거 커밋만 부모로 설정합니다.

```text
A 생성
B 생성: 부모 A
C 생성: 부모 B
```

과거 커밋 A가 새 커밋 C를 다시 부모로 가지도록 변경하는 기능은 존재하지 않습니다.

따라서 다음과 같은 순환은 만들어지지 않습니다.

```text
A -> B -> C -> A
```

### Graph

브랜치가 분기되면 단순한 하나의 연결 리스트가 아니라 여러 경로가 만들어집니다.

```text
          B
         /
A
         \
          C
```

따라서 커밋 구조는 방향이 있고 순환이 없는 그래프, 즉 DAG입니다.

---

## 21. 사이클이 생기면 발생하는 문제

커밋 그래프에 사이클이 생긴다고 가정합니다.

```text
A -> B -> C -> A
```

다음 문제가 발생할 수 있습니다.

- 조상과 후손의 시간적 관계가 깨짐
- 어떤 커밋이 먼저인지 결정하기 어려움
- 부모 우선 로그 순서를 만들 수 없음
- 위상 정렬 불가능
- 방문 처리가 없으면 탐색이 무한 반복될 수 있음
- 커밋 이력을 과거 방향으로 추적한다는 Git의 의미가 사라짐

따라서 커밋 그래프는 반드시 DAG 구조여야 합니다.

---

## 22. 부모-자식 인접 리스트

각 `Commit` 객체에는 부모 정보가 저장됩니다.

```python
commit.parents
```

예:

```text
A <- B <- C
```

부모 정보:

```python
B.parents = ["A"]
C.parents = ["B"]
```

그러나 `PATH`는 부모-자식 연결을 무방향 간선으로 처리해야 합니다.

즉 다음 이동이 모두 가능해야 합니다.

```text
자식 -> 부모
부모 -> 자식
```

부모 정보만 사용하면 부모에서 자식을 찾기 위해 모든 커밋을 순회해야 합니다.

이를 방지하기 위해 별도의 자식 인접 리스트를 관리합니다.

```python
self.children: dict[str, list[str]] = {}
```

예:

```python
children = {
    "A": ["B"],
    "B": ["C"],
    "C": [],
}
```

커밋 생성 시 부모의 자식 목록을 갱신합니다.

```python
for parent_hash in parents:
    self.children[parent_hash].append(commit_hash)
```

---

## 23. LOG 부모 우선 출력

일반 Git 로그는 보통 최신 커밋부터 출력합니다.

하지만 이 프로젝트에서는 학습 목적상 부모 커밋이 자식 커밋보다 먼저 출력되어야 합니다.

그래프:

```text
A <- B <- C
```

필요한 출력:

```text
A
B
C
```

잘못된 출력:

```text
C
B
A
```

---

## 24. DFS 기반 부모 우선 순서

현재 커밋을 결과에 추가하기 전에 모든 부모를 먼저 방문합니다.

```python
for parent_hash in commit.parents:
    _visit_commit_for_log(parent_hash)

result.append(commit_hash)
```

C부터 탐색하면 다음과 같이 동작합니다.

```text
visit C
    visit B
        visit A
            add A
        add B
    add C
```

결과:

```text
A
B
C
```

이 방식은 DFS 기반 위상 정렬 성격의 출력입니다.

---

## 25. 브랜치 그래프의 LOG 순서

그래프:

```text
          B
         /
A
         \
          C
```

가능한 출력:

```text
A
B
C
```

또는:

```text
A
C
B
```

B와 C 사이에는 부모-자식 관계가 없기 때문에 상대적 순서는 자유입니다.

그러나 A는 B와 C의 부모이므로 반드시 먼저 출력되어야 합니다.

---

## 26. LOG의 visited 집합

같은 커밋을 반복 처리하지 않기 위해 `visited` 집합을 사용합니다.

```python
visited: set[str] = set()
```

이미 방문한 커밋이면 다시 처리하지 않습니다.

```python
if commit_hash in visited:
    return
```

이 구조는 추후 merge처럼 여러 경로가 같은 조상에 도달하는 그래프에서도 중복 출력을 방지할 수 있습니다.

LOG 시간복잡도:

```text
O(V + E)
```

- V: 커밋 수
- E: 부모-자식 연결 수

---

## 27. Merge Sort 직접 구현

정렬 기능에서는 다음 표준 API를 사용하지 않았습니다.

```python
sorted()
list.sort()
```

대신 Merge Sort를 직접 구현하였습니다.

Merge Sort는 분할 정복 방식의 정렬 알고리즘입니다.

처리 과정:

```text
리스트를 절반으로 분할
    ↓
왼쪽 절반 정렬
    ↓
오른쪽 절반 정렬
    ↓
두 정렬된 리스트 병합
```

예:

```text
[D, B, A, C]
```

분할:

```text
[D, B]    [A, C]
```

다시 분할:

```text
[D] [B]   [A] [C]
```

병합:

```text
[B, D]    [A, C]
```

최종 결과:

```text
[A, B, C, D]
```

---

## 28. Merge Sort 분할

리스트 길이가 1 이하이면 이미 정렬된 상태입니다.

```python
if len(items) <= 1:
    return items[:]
```

중간 위치를 계산합니다.

```python
middle = len(items) // 2
```

왼쪽과 오른쪽을 재귀적으로 정렬합니다.

```python
left_half = merge_sort(
    items[:middle],
    comes_before_or_equal,
)

right_half = merge_sort(
    items[middle:],
    comes_before_or_equal,
)
```

---

## 29. Merge Sort 병합

두 리스트의 현재 원소를 비교합니다.

```python
if comes_before_or_equal(left_item, right_item):
    result.append(left_item)
    left_index += 1
else:
    result.append(right_item)
    right_index += 1
```

한쪽 리스트를 모두 사용한 뒤 나머지 리스트의 원소를 추가합니다.

```python
while left_index < len(left):
    result.append(left[left_index])
    left_index += 1
```

```python
while right_index < len(right):
    result.append(right[right_index])
    right_index += 1
```

---

## 30. 날짜 정렬

명령어:

```text
LOG --sort-by=date
```

timestamp가 빠른 커밋을 먼저 배치합니다.

```python
if first.timestamp == second.timestamp:
    return first.hash <= second.hash

return first.timestamp < second.timestamp
```

timestamp가 같으면 hash를 동률 처리 기준으로 사용합니다.

테스트 파일은 매우 빠르게 실행되기 때문에 여러 커밋이 같은 초에 생성될 수 있습니다.

이 경우 hash 비교를 통해 항상 같은 규칙으로 순서를 결정합니다.

---

## 31. 작성자 정렬

명령어:

```text
LOG --sort-by=author
```

작성자 이름을 소문자로 변환하여 비교합니다.

```python
first_author = first.author.lower()
second_author = second.author.lower()
```

작성자가 다르면 이름의 사전순으로 배치합니다.

```python
if first_author != second_author:
    return first_author < second_author
```

작성자가 같으면 timestamp를 비교합니다.

```python
if first.timestamp != second.timestamp:
    return first.timestamp < second.timestamp
```

timestamp도 같으면 hash를 마지막 동률 처리 기준으로 사용합니다.

```python
return first.hash <= second.hash
```

현재 프로그램에서는 한 번의 `INIT`으로 현재 사용자가 설정되고, 사용자를 변경하는 별도 명령은 없습니다.

따라서 일반적인 한 세션에서는 같은 작성자의 커밋이 생성되지만, 작성자 비교 알고리즘 자체는 서로 다른 작성자 데이터도 정렬할 수 있도록 구현되어 있습니다.

---

## 32. 비교 함수 재사용

정렬 알고리즘 자체는 한 번만 구현하였습니다.

```python
merge_sort(
    commits,
    comparison_function,
)
```

날짜 정렬:

```python
self._date_before_or_equal
```

작성자 정렬:

```python
self._author_before_or_equal
```

비교 함수만 변경하여 동일한 Merge Sort를 여러 기준에 재사용합니다.

---

## 33. Merge Sort 시간복잡도

| 경우 | 시간복잡도 |
|---|---:|
| 최선 | O(n log n) |
| 평균 | O(n log n) |
| 최악 | O(n log n) |

리스트를 절반씩 분할하므로 재귀 깊이는 다음과 같습니다.

```text
O(log n)
```

각 깊이에서 전체 n개의 원소를 병합합니다.

```text
O(n) × O(log n)
= O(n log n)
```

추가 공간복잡도:

```text
O(n)
```

병합 결과를 저장하는 별도의 리스트가 필요하기 때문입니다.

---

## 34. 안정 정렬 여부

본 Merge Sort는 안정 정렬입니다.

비교 결과가 같을 때 왼쪽 리스트의 원소를 먼저 선택합니다.

```python
if comes_before_or_equal(left_item, right_item):
    result.append(left_item)
```

왼쪽 원소는 원래 입력에서도 오른쪽의 같은 값보다 앞에 있었습니다.

따라서 같은 비교 값을 가진 원소들의 기존 상대적 순서가 유지됩니다.

---

## 35. PATH 최단 경로

명령어:

```text
PATH <commit1> <commit2>
```

두 커밋 사이의 최단 경로를 탐색합니다.

최단 경로는 지나가는 부모-자식 간선 수가 가장 적은 경로입니다.

그래프:

```text
A <- B <- C
```

다음 이동이 모두 가능합니다.

```text
A -> B
B -> A
B -> C
C -> B
```

부모-자식 관계를 무방향 간선으로 간주하기 때문입니다.

---

## 36. PATH에서 BFS를 사용하는 이유

모든 부모-자식 간선의 비용은 1입니다.

```text
커밋 하나 이동 = 비용 1
```

BFS는 시작점에서 가까운 거리부터 탐색합니다.

```text
거리 0
거리 1
거리 2
거리 3
...
```

따라서 가중치가 없는 그래프에서 최소 간선 수 경로를 찾는 데 적합합니다.

DFS는 하나의 경로를 끝까지 먼저 탐색하기 때문에 처음 발견한 경로가 최단 경로라고 보장할 수 없습니다.

---

## 37. PATH 큐 구조

BFS 큐에는 현재 경로 전체를 저장합니다.

```python
queue: deque[list[str]] = deque()
queue.append([start_hash])
```

A에서 시작:

```python
[
    ["A"]
]
```

B로 이동:

```python
[
    ["A", "B"]
]
```

C로 이동:

```python
[
    ["A", "B", "C"]
]
```

목적지에 도달하면 현재 리스트 자체가 경로가 됩니다.

---

## 38. PATH 이웃 탐색

한 커밋의 이웃에는 부모와 자식이 모두 포함됩니다.

```python
for parent_hash in commit.parents:
    neighbors.append(parent_hash)
```

```python
for child_hash in children.get(commit_hash, []):
    neighbors.append(child_hash)
```

이 때문에 `Commit.parents`와 `children` 인접 리스트가 모두 필요합니다.

---

## 39. PATH 순환 방지

무방향 그래프에서는 같은 연결을 앞뒤로 반복할 수 있습니다.

```text
A -> B -> A -> B
```

이를 방지하기 위해 현재 경로에 이미 존재하는 커밋은 다시 추가하지 않습니다.

```python
if neighbor_hash in current_path:
    continue
```

---

## 40. PATH 최단 거리 관리

각 커밋에 도달한 가장 짧은 거리를 저장합니다.

```python
best_distance: dict[str, int] = {
    start_hash: 0,
}
```

새 경로가 이전 거리보다 짧거나 같은 경우 큐에 추가합니다.

```python
if (
    previous_distance is None
    or next_distance <= previous_distance
):
    best_distance[neighbor_hash] = next_distance
    queue.append(current_path + [neighbor_hash])
```

같은 거리를 허용하는 이유는 동일한 길이의 최단 경로가 여러 개 존재할 수 있기 때문입니다.

---

## 41. 사전순 최소 경로

최단 경로가 여러 개라면 각 경로를 문자열로 변환합니다.

```text
hash1->hash2->hash3
```

예:

```text
aaa111->bbb222->ddd444
aaa111->ccc333->ddd444
```

문자열을 직접 비교합니다.

```python
if path_text < smallest_text:
    smallest_path = path
```

표준 정렬 API를 사용하지 않고 가장 작은 경로를 선택합니다.

경로가 존재하지 않으면 다음을 출력합니다.

```text
No path
```

일반적인 BFS 시간복잡도:

```text
O(V + E)
```

현재 구현은 동일 길이의 여러 최단 경로를 저장할 수 있으므로, 동률 경로가 매우 많은 그래프에서는 일반 BFS보다 추가 메모리를 사용할 수 있습니다.

---

## 42. ANCESTORS 조상 탐색

명령어:

```text
ANCESTORS <commit_hash>
```

해당 커밋에서 부모 방향으로 도달할 수 있는 모든 커밋을 출력합니다.

그래프:

```text
A <- B <- C
```

입력:

```text
ANCESTORS C
```

결과에는 다음이 포함됩니다.

```text
A
B
```

C 자신은 자신의 조상이 아니므로 포함하지 않습니다.

---

## 43. ANCESTORS의 DFS

대상 커밋의 부모부터 탐색을 시작합니다.

```python
for parent_hash in commit.parents:
    _visit_ancestor(parent_hash)
```

현재 조상을 결과에 추가하기 전에 더 오래된 부모를 먼저 방문합니다.

```python
for parent_hash in commit.parents:
    _visit_ancestor(parent_hash)

result.append(commit_hash)
```

따라서 가능한 한 오래된 조상부터 출력됩니다.

---

## 44. ANCESTORS의 visited

여러 부모 경로가 같은 조상에 도달할 수 있습니다.

```text
        B
       / \
A <---   D
       \ /
        C
```

D의 조상을 탐색하면 A에 두 번 도달할 수 있습니다.

이를 방지하기 위해 `visited`를 사용합니다.

```python
if commit_hash in visited:
    return
```

각 조상 커밋은 한 번만 처리됩니다.

시간복잡도:

```text
O(V + E)
```

여기서 V와 E는 해당 커밋에서 도달 가능한 조상 부분 그래프를 의미합니다.

---

## 45. 역색인

검색 시 모든 커밋을 순회하지 않고 역색인을 사용합니다.

두 종류의 인덱스를 지원합니다.

```text
keyword -> commit hash 목록
author -> commit hash 목록
```

커밋 생성 시점에 인덱스를 미리 갱신합니다.

```text
COMMIT 생성
    ↓
Commit 저장
    ↓
_update_indexes(commit)
    ↓
keyword_index 갱신
    ↓
author_index 갱신
```

---

## 46. 키워드 역색인

커밋 메시지는 다음 방식으로 정규화합니다.

```python
message_tokens = commit.message.lower().split()
```

예:

```text
Add Login Feature
```

토큰:

```python
[
    "add",
    "login",
    "feature",
]
```

인덱스:

```python
keyword_index = {
    "add": ["abc123"],
    "login": ["abc123"],
    "feature": ["abc123"],
}
```

---

## 47. 중복 키워드 처리

메시지에 같은 단어가 반복될 수 있습니다.

```text
Fix login login login
```

그대로 저장하면 같은 hash가 중복될 수 있습니다.

```python
"login": [
    "abc123",
    "abc123",
    "abc123",
]
```

이를 방지하기 위해 한 커밋을 처리하는 동안 이미 추가한 토큰을 `set`으로 관리합니다.

```python
added_tokens: set[str] = set()
```

이미 처리한 토큰이면 건너뜁니다.

```python
if token in added_tokens:
    continue
```

결과:

```python
"login": ["abc123"]
```

---

## 48. 작성자 역색인

작성자 이름은 소문자로 정규화합니다.

```python
author_key = commit.author.lower()
```

작성자:

```text
Alice Kim
```

인덱스 key:

```text
alice kim
```

따라서 다음 검색은 모두 같은 결과를 반환합니다.

```text
SEARCH "--author=Alice Kim"
SEARCH "--author=alice kim"
SEARCH "--author=ALICE KIM"
```

원래 이름은 `Commit.author`에 보존되므로 출력에는 `Alice Kim`이 표시됩니다.

---

## 49. 여러 키워드 검색

다음 검색도 지원합니다.

```text
SEARCH "login feature"
```

검색어를 토큰으로 분리합니다.

```python
query_tokens = keyword.strip().lower().split()
```

결과:

```python
[
    "login",
    "feature",
]
```

첫 번째 토큰의 인덱스 목록을 후보로 가져옵니다.

```python
candidate_hashes = self.keyword_index["login"][:]
```

다음 토큰의 목록과 교집합에 해당하는 커밋만 남깁니다.

```text
login 토큰 포함
AND
feature 토큰 포함
```

이 기능은 정확히 연속된 `"login feature"` 문자열을 찾는 것이 아니라 두 토큰을 모두 포함한 커밋을 찾습니다.

---

## 50. 역색인이 순회 검색보다 빠른 이유

순회 검색 방식:

```python
for commit in self.commits.values():
    if keyword in commit.message:
        ...
```

커밋이 n개라면 검색마다 모든 커밋을 확인해야 합니다.

```text
O(n)
```

역색인 방식:

```python
commit_hashes = self.keyword_index.get(keyword, [])
```

딕셔너리 조회의 평균 시간:

```text
O(1)
```

검색 결과가 r개라면 출력까지 포함한 일반적인 비용:

```text
O(1 + r)
```

단, 커밋 생성 시 메시지 토큰 수 k에 비례하여 인덱스를 갱신해야 합니다.

```text
O(k)
```

즉 검색을 빠르게 하기 위해 커밋을 저장할 때 미리 추가 작업을 수행하는 구조입니다.

---

## 51. 검색 결과 형식

검색 결과가 존재할 때:

```text
Found 2 commit(s):
- 9df1dd: Add login feature (Alice Kim)
- f50ac9: Fix login button (Alice Kim)
```

검색 결과가 없을 때:

```text
Found 0 commits
```

키워드 검색과 작성자 검색은 동일한 `_format_search_results()`를 사용합니다.

---

## 52. 브랜치 라벨 출력

LOG에서 브랜치가 현재 가리키는 커밋에는 브랜치 이름을 표시합니다.

```text
commit 6395a7 (Alice, 2026-07-28 15:52:00) [feature]
Add login feature
```

모든 브랜치를 확인하여 HEAD가 해당 커밋과 같은지 검사합니다.

```python
for branch_name, branch_head in self.branches.items():
    if branch_head == commit_hash:
        labels.append(branch_name)
```

여러 브랜치가 같은 커밋을 가리키면 모두 표시할 수 있습니다.

```text
[main, feature]
```

브랜치 라벨은 브랜치의 현재 HEAD에만 표시됩니다.

---

## 53. 에러 처리

### 저장소 초기화 전 명령

```text
Repository not initialized
```

### 잘못된 인자

```text
Invalid args
```

### 존재하지 않는 브랜치

```text
Unknown branch: <name>
```

### 중복 브랜치

```text
Branch already exists: <name>
```

### 존재하지 않는 커밋

```text
Unknown commit: <hash>
```

### 알 수 없는 명령어

```text
Unknown command: <command>
```

### 커밋이 없는 LOG

```text
No commits
```

### 조상이 없는 커밋

```text
No ancestors
```

### 연결 경로가 없는 경우

```text
No path
```

---

## 54. 전체 커밋 생성 흐름

```text
사용자 입력
    ↓
main.py
    ↓
shlex.split()
    ↓
execute_command()
    ↓
MiniGit.create_commit()
    ↓
현재 branch HEAD 조회
    ↓
부모 목록 생성
    ↓
commit hash 생성
    ↓
Commit 객체 생성
    ↓
commits 딕셔너리에 저장
    ↓
현재 branch HEAD 이동
    ↓
children 인접 리스트 갱신
    ↓
keyword_index 갱신
    ↓
author_index 갱신
    ↓
결과 문자열 반환
    ↓
터미널 출력
```

---

## 55. 명령어별 내부 흐름

### INIT

```text
INIT
  ↓
저장소 상태 초기화
  ↓
main 브랜치 생성
  ↓
current_branch = main
  ↓
current_user 설정
```

### BRANCH

```text
BRANCH feature
  ↓
현재 HEAD 조회
  ↓
feature가 같은 HEAD를 가리키도록 저장
```

### SWITCH

```text
SWITCH feature
  ↓
브랜치 존재 여부 확인
  ↓
current_branch = feature
```

### COMMIT

```text
COMMIT message
  ↓
현재 HEAD를 부모로 설정
  ↓
고유 hash 생성
  ↓
Commit 저장
  ↓
현재 브랜치 HEAD 이동
  ↓
children 및 역색인 갱신
```

### LOG

```text
LOG
  ↓
모든 커밋 확인
  ↓
DFS로 부모 먼저 방문
  ↓
부모 우선 순서 출력
```

### LOG --sort-by

```text
LOG --sort-by=date|author
  ↓
커밋 객체 목록 생성
  ↓
비교 함수 선택
  ↓
Merge Sort 실행
  ↓
정렬 결과 출력
```

### PATH

```text
PATH commit1 commit2
  ↓
두 커밋 존재 여부 확인
  ↓
부모 + 자식 이웃 조회
  ↓
BFS 실행
  ↓
모든 최단 경로 확인
  ↓
사전순 최소 경로 선택
```

### ANCESTORS

```text
ANCESTORS hash
  ↓
대상 커밋 존재 여부 확인
  ↓
부모 방향 DFS
  ↓
visited로 중복 방지
  ↓
모든 조상 출력
```

### SEARCH

```text
SEARCH keyword
  ↓
검색어 소문자 변환 및 split
  ↓
keyword_index 조회
  ↓
후보 commit hash 확인
  ↓
검색 결과 출력
```

---

## 56. 시간복잡도

| 기능 | 자료구조 또는 알고리즘 | 시간복잡도 |
|---|---|---:|
| commit hash 조회 | Dictionary | 평균 O(1) |
| 브랜치 HEAD 조회 | Dictionary | 평균 O(1) |
| 브랜치 생성 | Dictionary | 평균 O(1) |
| 브랜치 전환 | Dictionary | 평균 O(1) |
| 커밋 생성 | Dictionary + 인덱스 갱신 | 평균 O(k) |
| 부모 우선 LOG | DFS | O(V + E) |
| 조상 탐색 | DFS | O(V + E) |
| 일반 최단 경로 탐색 | BFS | O(V + E) |
| 날짜 정렬 | Merge Sort | O(n log n) |
| 작성자 정렬 | Merge Sort | O(n log n) |
| 단일 키워드 검색 | 역색인 | 평균 O(1 + r) |
| 작성자 검색 | 역색인 | 평균 O(1 + r) |
| 브랜치 라벨 확인 | 브랜치 순회 | O(b) |

기호:

```text
k = 커밋 메시지 토큰 수
r = 검색 결과 수
V = 커밋 수
E = 부모-자식 연결 수
n = 정렬 대상 커밋 수
b = 브랜치 수
```

---

## 57. 알고리즘 로직 분리

그래프 탐색과 정렬 로직은 별도의 파일로 분리하였습니다.

```text
mini_git.py
    저장소 상태 관리
    명령어 기능 연결
    결과 포맷 생성

algorithms/graph.py
    LOG용 부모 우선 DFS
    PATH용 BFS
    ANCESTORS용 DFS

algorithms/sorting.py
    Merge Sort
```

예:

```python
path = find_shortest_path(
    start_hash=start_hash,
    end_hash=end_hash,
    commits=self.commits,
    children=self.children,
)
```

`mini_git.py`는 필요한 데이터를 전달하고, 실제 그래프 탐색은 `graph.py`에서 수행합니다.

이 구조를 통해 알고리즘을 CLI 코드와 독립적으로 이해하고 테스트할 수 있습니다.

---

## 58. docstring과 주석 작성 기준

주요 클래스와 함수의 docstring에는 다음 내용을 작성하였습니다.

- 함수 또는 클래스의 역할
- 사용한 알고리즘
- 중요한 매개변수
- 반환값
- 시간복잡도
- 일반적이지 않은 설계 선택

예:

```python
def find_shortest_path(...):
    """
    Find a shortest path between two commits using BFS.

    Parent-child connections are treated as undirected connections.
    """
```

주석은 코드만으로 이해하기 어려운 이유를 설명할 때 사용하였습니다.

```python
# Prevent cycles inside the current path.
if neighbor_hash in current_path:
    continue
```

단순히 코드 내용을 그대로 반복하는 주석은 최소화하였습니다.

---

## 59. 테스트 파일

### `tests/basic_commands.txt`

검증 기능:

- INIT
- COMMIT
- BRANCH
- SWITCH
- LOG
- 날짜 정렬
- 작성자 정렬
- 프로그램 종료

실행:

```bash
python main.py < tests/basic_commands.txt
```

---

### `tests/branch_commands.txt`

검증 기능:

- 같은 커밋에서 브랜치 분기
- 브랜치별 HEAD 독립 관리
- 부모 커밋 우선 출력

실행:

```bash
python main.py < tests/branch_commands.txt
```

---

### `tests/search_commands.txt`

검증 기능:

- 단일 키워드 검색
- 대소문자 무시
- 여러 키워드 검색
- 결과 없음
- 작성자 검색
- 공백 포함 작성자 검색

실행:

```bash
python main.py < tests/search_commands.txt
```

---

### `tests/error_commands.txt`

검증 기능:

- INIT 전 명령 실행
- 인자 누락
- 인자 초과
- 중복 브랜치 생성
- 존재하지 않는 브랜치
- 잘못된 정렬 옵션
- 존재하지 않는 커밋
- 지원하지 않는 명령어

실행:

```bash
python main.py < tests/error_commands.txt
```

---

## 60. 전체 자동 테스트

다음 명령으로 테스트 파일을 순서대로 실행할 수 있습니다.

```bash
python main.py < tests/basic_commands.txt
python main.py < tests/branch_commands.txt
python main.py < tests/search_commands.txt
python main.py < tests/error_commands.txt
```

테스트 파일 마지막에는 `quit`이 포함되어 있어 각 테스트가 자동으로 종료됩니다.

리다이렉션 테스트에서는 명령이 매우 빠르게 실행되기 때문에 여러 커밋의 timestamp가 같은 초로 출력될 수 있습니다.

이 경우에도 정렬 함수는 실행되며, timestamp가 같으면 hash를 동률 처리 기준으로 사용합니다.

---

## 61. PATH와 ANCESTORS 수동 테스트

commit hash는 실행할 때마다 달라지므로 실제 생성된 hash를 사용합니다.

실행:

```bash
python main.py
```

입력:

```text
INIT "Alice"
COMMIT "Commit A"
COMMIT "Commit B"
COMMIT "Commit C"
```

예시 출력:

```text
[main aa1111] Commit A
[main bb2222] Commit B
[main cc3333] Commit C
```

PATH 테스트:

```text
PATH aa1111 cc3333
```

예상 결과:

```text
Path: aa1111 -> bb2222 -> cc3333
```

ANCESTORS 테스트:

```text
ANCESTORS cc3333
```

결과에는 Commit A와 Commit B가 포함되어야 합니다.

첫 커밋 테스트:

```text
ANCESTORS aa1111
```

예상 결과:

```text
No ancestors
```

실제 hash는 실행마다 다르게 생성됩니다.

---

## 62. 문법 검사

모든 Python 파일의 문법을 확인합니다.

```bash
python -m py_compile \
main.py \
mini_git.py \
models/commit.py \
algorithms/graph.py \
algorithms/sorting.py
```

오류가 없으면 아무 내용도 출력되지 않습니다.

---

## 63. 정렬 API 제한 확인

프로젝트 코드에서 금지된 표준 정렬 API를 사용하지 않았는지 확인합니다.

```bash
grep -R "sorted(" --include="*.py" --exclude-dir=".venv" .
grep -R "\.sort(" --include="*.py" --exclude-dir=".venv" .
```

아무 결과도 출력되지 않으면 프로젝트 Python 코드에서 `sorted()`와 `.sort()`를 사용하지 않은 것입니다.

`.venv`를 제외하지 않으면 pip 등 외부 패키지 코드에서 `sorted()`가 발견될 수 있습니다.

해당 코드는 프로젝트에서 직접 작성한 코드가 아니므로 검사 시 `.venv`를 제외합니다.

---

# 평가요소 대응

## 64. 평가 항목 1: 필수 기능

| 평가 질문 | 구현 내용 | 관련 코드 |
|---|---|---|
| INIT 후 main, HEAD, 사용자가 설정되는가? | `main: None`, 현재 브랜치, 현재 사용자 설정 | `init_repository()` |
| BRANCH와 SWITCH가 동작하는가? | 현재 HEAD를 가리키는 브랜치 생성 후 현재 브랜치 변경 | `create_branch()`, `switch_branch()` |
| COMMIT이 해당 브랜치에 반영되는가? | 현재 브랜치 HEAD만 새 커밋으로 이동 | `create_commit()` |
| LOG가 부모를 먼저 출력하는가? | 부모 방문 후 현재 커밋 추가 | `topological_commit_order()` |
| PATH가 최단 경로를 출력하는가? | 무방향 그래프 BFS | `find_shortest_path()` |
| 경로가 없으면 No path인가? | BFS 결과가 없으면 `No path` 반환 | `show_path()` |
| ANCESTORS가 모든 조상을 출력하는가? | 부모 방향 DFS와 visited 사용 | `find_all_ancestors()` |
| SEARCH가 동작하는가? | keyword 및 author 역색인 사용 | `search_keyword()`, `search_author()` |
| 정렬 명령이 동작하는가? | 직접 구현한 Merge Sort 사용 | `show_sorted_log()` |

---

## 65. 평가 항목 2: 구조와 책임

### 저장소, 브랜치, HEAD, 사용자 분리

```text
commits
    전체 커밋 객체 저장

branches
    브랜치 이름별 HEAD hash 저장

current_branch
    현재 선택된 브랜치 저장

current_user
    커밋 작성자 저장
```

각 자료구조는 하나의 명확한 책임을 가집니다.

브랜치는 커밋 전체 목록을 저장하지 않고 HEAD hash 하나만 저장합니다.

---

### 빠른 hash 조회

```python
self.commits: dict[str, Commit]
```

commit hash를 key로 사용하여 평균 O(1)에 조회합니다.

---

### hash 충돌 방지

- 카운터를 hash 입력에 포함
- SHA-1 앞 6자리 사용
- 이미 존재하는 hash인지 확인
- 중복이면 카운터 증가 후 재생성

---

### 역색인 갱신 시점

역색인은 검색 시점이 아니라 `COMMIT` 생성 시점에 갱신합니다.

```python
self._update_indexes(commit)
```

따라서 검색 시 모든 커밋을 순회하지 않습니다.

---

### 그래프 알고리즘 재사용

```text
graph.py
├── LOG용 탐색
├── PATH용 탐색
└── ANCESTORS용 탐색
```

알고리즘을 저장소 관리 코드에서 분리하여 독립적으로 사용할 수 있도록 구성하였습니다.

---

## 66. 평가 항목 3: 그래프 알고리즘

### DAG여야 하는 이유

- 커밋은 과거 부모를 가리키는 방향성을 가짐
- 새 커밋은 이미 존재하는 커밋만 부모로 지정
- 순환이 생기면 부모 우선 순서 결정 불가능
- 위상 정렬 불가능
- 조상 관계의 의미가 깨짐
- 탐색이 무한 반복될 수 있음

---

### LOG의 부모 우선 방식

DFS로 부모를 먼저 방문한 후 현재 커밋을 결과에 추가합니다.

```python
visit(parents)
result.append(current)
```

이 방식으로 모든 부모가 자식보다 먼저 출력됩니다.

---

### PATH에서 BFS를 선택한 이유

모든 간선 비용이 1이므로 BFS가 최소 간선 수 경로를 보장합니다.

---

### 간선을 무방향으로 정의한 이유

PATH는 오래된 커밋에서 새로운 커밋으로도, 새로운 커밋에서 오래된 커밋으로도 이동할 수 있어야 합니다.

따라서 부모와 자식을 모두 이웃으로 사용합니다.

---

## 67. 평가 항목 4: 분석과 응용

### 정렬 알고리즘의 평균 및 최악 시간복잡도

Merge Sort:

```text
평균 O(n log n)
최악 O(n log n)
최선 O(n log n)
```

---

### 안정 정렬 여부

같은 값일 때 왼쪽 원소를 먼저 선택하므로 기존 상대적 순서가 유지됩니다.

따라서 안정 정렬입니다.

---

### 역색인이 순회 검색보다 빠른 이유

순회 검색:

```text
O(n)
```

역색인:

```text
평균 O(1 + r)
```

- O(1): 딕셔너리에서 후보 목록 조회
- r: 실제 검색 결과 처리

---

## 68. 커밋 수가 10배 증가했을 때의 병목

### LOG

모든 커밋을 출력해야 하므로 커밋 수 증가에 비례해 처리량과 출력량이 증가합니다.

```text
O(V + E)
```

개선 방향:

- 페이지네이션
- 출력 개수 제한
- 특정 브랜치 또는 범위만 출력
- 위상 순서 캐싱

---

### PATH

현재 구현은 큐에 경로 전체를 저장합니다.

```python
queue.append(current_path + [neighbor_hash])
```

커밋 수가 증가하면 경로 리스트 복사로 메모리 사용량이 커질 수 있습니다.

개선 방향:

```text
큐에는 commit hash만 저장
    ↓
previous 딕셔너리에 이전 노드 저장
    ↓
목적지 도착 후 역추적
```

예:

```python
previous = {
    "B": "A",
    "C": "B",
}
```

---

### 브랜치 라벨

현재 LOG 출력 시 각 커밋마다 전체 브랜치를 확인합니다.

```text
O(n × b)
```

- n: 출력 커밋 수
- b: 브랜치 수

개선 방향:

```text
commit hash -> branch 목록
```

역방향 인덱스를 추가합니다.

---

### 역색인

커밋 수가 많아지면 인덱스 목록과 메모리 사용량도 증가합니다.

개선 방향:

- 토큰 정규화 강화
- 불필요한 공통 단어 제외
- 데이터베이스 인덱스 사용
- 파일 또는 데이터베이스 영속성 도입

---

## 69. PATH를 부모 방향으로만 바꿀 경우

현재 PATH:

```text
부모 -> 자식
자식 -> 부모
```

부모 방향만 허용하면 현재 커밋에서 과거 커밋으로만 이동할 수 있습니다.

그래프:

```text
A <- B <- C
```

가능:

```text
C -> B -> A
```

불가능:

```text
A -> B -> C
```

변경해야 하는 부분은 `_get_neighbors()`입니다.

현재:

```python
for parent_hash in commit.parents:
    neighbors.append(parent_hash)

for child_hash in children.get(commit_hash, []):
    neighbors.append(child_hash)
```

부모 방향만 허용할 경우:

```python
for parent_hash in commit.parents:
    neighbors.append(parent_hash)
```

BFS 알고리즘은 유지할 수 있지만 탐색 가능한 방향이 달라집니다.

`children` 인접 리스트도 PATH 탐색에서는 필요하지 않게 됩니다.

---

## 70. 작성자 정렬에 부모 우선 조건까지 추가된다면

현재 `LOG --sort-by=author`는 작성자 기준으로 전체 커밋을 정렬합니다.

요구사항이 다음 두 조건을 동시에 요구한다고 가정합니다.

```text
1. 부모는 반드시 자식보다 먼저
2. 현재 출력 가능한 커밋 중 작성자가 빠른 커밋 먼저
```

이 경우 일반 Merge Sort만으로는 부모-자식 제약을 함께 보장하기 어렵습니다.

사용 가능한 전략:

```text
Kahn 방식 위상 정렬
    +
현재 출력 가능한 커밋의 작성자 우선순위
```

처리 과정:

```text
각 커밋의 진입 차수 계산
    ↓
부모가 모두 출력된 커밋만 후보로 추가
    ↓
후보 중 작성자 이름이 가장 빠른 커밋 선택
    ↓
해당 커밋 출력
    ↓
자식의 진입 차수 감소
    ↓
새로운 후보 추가
```

표준 정렬 API가 금지되어 있으므로 다음 중 하나를 사용할 수 있습니다.

- 후보 목록을 직접 선형 탐색
- 직접 구현한 우선순위 큐
- 직접 구현한 Heap

---

## 71. 카운터 기반 hash와 난수 기반 hash 비교

### 카운터 기반

장점:

- 생성 순서를 추적하기 쉬움
- 테스트 흐름을 이해하기 쉬움
- 디버깅이 비교적 쉬움
- 중복 방지 논리가 명확함

단점:

- 실제 Git의 내용 기반 hash와 차이가 큼
- 카운터 값이 hash 입력에 영향을 줌

---

### 난수 기반

장점:

- 매번 다른 값 생성 가능
- 구현이 단순할 수 있음

단점:

- 실행마다 결과가 달라짐
- 테스트 재현성이 낮음
- 디버깅 시 같은 상황을 재현하기 어려움
- 예상 hash를 테스트에 고정하기 어려움
- 충돌 검사가 여전히 필요함

---

### 현재 방식

현재 구현은 다음 정보를 사용합니다.

```text
counter
message
author
timestamp
SHA-1
```

카운터를 통해 hash 입력을 매번 다르게 만들고, 최종적으로 기존 저장소에 같은 hash가 있는지도 확인합니다.

---

## 72. 실제 Git과 Mini Git의 차이

| 항목 | 실제 Git | Mini Git |
|---|---|---|
| 파일 내용 | Blob 객체로 저장 | 저장하지 않음 |
| 디렉터리 | Tree 객체로 저장 | 저장하지 않음 |
| commit hash | 객체 내용 전체 기반 | counter, message, author, timestamp 기반 |
| hash 길이 | 전체 hash 사용 | 앞 6자리 사용 |
| 데이터 저장 | `.git` 디렉터리에 영속 저장 | 메모리에서만 동작 |
| 브랜치 | ref가 commit hash를 저장 | 딕셔너리에 HEAD hash 저장 |
| HEAD | ref 또는 commit을 가리킴 | 현재 브랜치 이름 저장 |
| Merge commit | 여러 부모 가능 | 자료구조만 지원, 명령 미구현 |
| Diff | 파일 차이 비교 | 미구현 |
| 네트워크 | push, pull, fetch | 미구현 |

---

## 73. 실행 예시

```text
mini-git> INIT "Alice"
Initialized repository.
Current branch: main
Current user: Alice

mini-git> COMMIT "Initial commit"
[main 254a69] Initial commit

mini-git> BRANCH feature
Created branch: feature

mini-git> SWITCH feature
Switched to branch: feature

mini-git> COMMIT "Add login feature"
[feature 6395a7] Add login feature

mini-git> SWITCH main
Switched to branch: main

mini-git> COMMIT "Add payment feature"
[main dfe969] Add payment feature

mini-git> LOG
commit 254a69 (Alice, 2026-07-28 15:52:00)
Initial commit

commit 6395a7 (Alice, 2026-07-28 15:52:00) [feature]
Add login feature

commit dfe969 (Alice, 2026-07-28 15:52:00) [main]
Add payment feature

mini-git> SEARCH login
Found 1 commit(s):
- 6395a7: Add login feature (Alice)

mini-git> quit
Mini Git closed.
```

commit hash와 timestamp는 실행할 때마다 달라질 수 있습니다.

---

## 74. 평가 시 코드 설명 순서

평가에서는 다음 순서로 설명할 수 있습니다.

```text
1. main.py
   - 사용자 입력
   - shlex 파싱
   - 명령어 분기

2. models/commit.py
   - Commit 필드
   - parents를 리스트로 만든 이유

3. mini_git.py의 __init__()
   - commits
   - branches
   - current_branch
   - current_user
   - children
   - 역색인

4. create_commit()
   - 부모 설정
   - hash 생성
   - Commit 저장
   - HEAD 이동
   - children 갱신
   - 역색인 갱신

5. algorithms/graph.py
   - LOG의 DFS
   - PATH의 BFS
   - ANCESTORS의 DFS

6. algorithms/sorting.py
   - Merge Sort 분할
   - 병합
   - 안정 정렬

7. search_keyword()
   - 역색인 검색
   - 순회 검색과 시간복잡도 비교

8. tests/
   - 기능별 테스트 결과
```

---

## 75. 평가요소 최종 점검표

### 항목 1: 필수 기능

- [x] INIT가 main 브랜치를 생성한다.
- [x] INIT가 현재 브랜치를 설정한다.
- [x] INIT가 현재 사용자를 설정한다.
- [x] BRANCH가 현재 HEAD를 가리키는 새 브랜치를 만든다.
- [x] SWITCH가 지정 브랜치로 전환한다.
- [x] COMMIT이 현재 브랜치 HEAD를 갱신한다.
- [x] LOG가 부모를 자식보다 먼저 출력한다.
- [x] PATH가 최단 경로를 출력한다.
- [x] PATH가 경로가 없을 때 `No path`를 반환한다.
- [x] ANCESTORS가 모든 조상을 출력한다.
- [x] SEARCH가 keyword 역색인을 사용한다.
- [x] SEARCH가 author 역색인을 사용한다.
- [x] 날짜 및 작성자 정렬이 동작한다.

### 항목 2: 구조와 품질

- [x] 저장소와 브랜치 상태를 분리하였다.
- [x] HEAD와 현재 사용자 정보를 분리하였다.
- [x] 커밋 저장소는 hash 기반 딕셔너리이다.
- [x] hash 충돌과 중복을 확인한다.
- [x] COMMIT 생성 시 역색인을 갱신한다.
- [x] 그래프 알고리즘을 별도 파일로 분리하였다.
- [x] 정렬 알고리즘을 별도 파일로 분리하였다.
- [x] 주요 함수와 클래스에 docstring을 작성하였다.

### 항목 3: 알고리즘 이해

- [x] 커밋 그래프가 DAG인 이유를 설명할 수 있다.
- [x] 사이클이 발생하면 생기는 문제를 설명할 수 있다.
- [x] LOG의 부모 우선 DFS를 설명할 수 있다.
- [x] PATH에 BFS를 선택한 이유를 설명할 수 있다.
- [x] PATH의 간선을 무방향으로 처리한 이유를 설명할 수 있다.
- [x] ANCESTORS의 DFS와 visited 역할을 설명할 수 있다.

### 항목 4: 분석과 응용

- [x] Merge Sort 평균 시간복잡도를 설명할 수 있다.
- [x] Merge Sort 최악 시간복잡도를 설명할 수 있다.
- [x] 안정 정렬인 이유를 설명할 수 있다.
- [x] 역색인이 순회 검색보다 빠른 이유를 설명할 수 있다.
- [x] 커밋 수 증가 시 병목을 예상할 수 있다.
- [x] PATH를 부모 방향으로 제한할 때의 변화를 설명할 수 있다.
- [x] 부모 우선과 작성자 정렬을 함께 처리하는 방법을 설명할 수 있다.
- [x] 카운터 기반과 난수 기반 hash의 차이를 설명할 수 있다.

### 항목 5: 보너스

- [ ] Diff
- [ ] Merge
- [ ] 정렬 알고리즘 성능 비교

보너스 과제는 선택사항이며 본 프로젝트에서는 구현하지 않았습니다.

---

## 76. 핵심 학습 내용

이 프로젝트를 통해 다음 내용을 직접 구현하고 확인하였습니다.

### 커밋 그래프

커밋은 단순한 최신순 목록이 아니라 부모 연결을 가진 DAG 구조입니다.

### 브랜치

브랜치는 전체 커밋 이력을 복사하지 않고 특정 커밋 hash 하나를 가리킵니다.

### HEAD

현재 선택된 브랜치 이름과 해당 브랜치가 가리키는 commit hash를 통해 현재 HEAD를 관리합니다.

### DFS

LOG의 부모 우선 출력과 ANCESTORS의 조상 탐색에 사용하였습니다.

### BFS

가중치가 없는 커밋 그래프에서 최소 간선 수 경로를 찾기 위해 사용하였습니다.

### Merge Sort

표준 정렬 API 없이 평균과 최악 모두 O(n log n)인 안정 정렬을 직접 구현하였습니다.

### 비교 함수

정렬 알고리즘은 그대로 유지하고 비교 함수만 변경하여 날짜와 작성자 기준 정렬에 재사용하였습니다.

### 역색인

검색할 때 전체 커밋을 순회하지 않고 키워드 또는 작성자에서 commit hash 목록을 바로 조회하도록 구현하였습니다.

### 시간복잡도

각 기능에 사용한 자료구조와 알고리즘이 입력 크기 증가에 따라 어떤 비용을 가지는지 분석하였습니다.