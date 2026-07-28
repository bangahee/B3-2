# B3-2 Mini Git 구축

Python으로 구현한 CLI 기반 Mini Git 프로그램입니다.

실제 Git의 모든 기능을 재현하는 대신, 커밋 메타데이터를 중심으로 Git의 핵심 구조인 커밋 그래프, 브랜치, HEAD, 그래프 탐색, 정렬 알고리즘, 역색인을 직접 구현하였습니다.

프로그램은 다음 흐름으로 동작합니다.

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

본 프로젝트에서는 다음 내용을 직접 구현하고 이해하는 것을 목표로 하였습니다.

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

## 2. 구현 기능

### 저장소 및 브랜치 관리

- `INIT <user_name>`
- `BRANCH <branch_name>`
- `SWITCH <branch_name>`
- `COMMIT <message>`

### 커밋 로그 및 탐색

- `LOG`
- `PATH <commit1> <commit2>`
- `ANCESTORS <commit_hash>`

### 검색 및 정렬

- `SEARCH <keyword>`
- `SEARCH --author=<name>`
- `LOG --sort-by=date`
- `LOG --sort-by=author`

### 프로그램 종료

- `exit`
- `quit`

---

## 3. 구현하지 않은 기능

본 프로젝트에서는 필수 기능과 핵심 알고리즘 구현에 집중하였습니다.

다음 기능은 구현하지 않았습니다.

- 실제 파일 내용 추적
- staging area
- Diff
- Merge 명령
- 두 개 이상의 정렬 알고리즘 성능 비교
- 데이터 영속성
- 네트워크 통신
- push / pull / fetch
- rebase
- cherry-pick

프로그램은 메모리에서만 동작합니다.

프로그램을 종료하면 생성한 커밋, 브랜치, 역색인 정보는 모두 사라집니다.

---

## 4. 개발 환경

- Python 3.10 이상
- CLI 기반 프로그램
- 외부 패키지 사용 없음
- 그래프 전용 라이브러리 사용 없음
- Python 표준 정렬 API 사용 없음
  - `sorted()` 사용 금지
  - `list.sort()` 사용 금지

사용한 기본 자료형:

- `list`
- `dict`
- `set`

사용한 표준 라이브러리:

- `datetime`
- `hashlib`
- `shlex`
- `collections.deque`
- `dataclasses`
- `ast`
- `pathlib`

---

## 5. 프로젝트 구조

```text
B3-2/
├── README.md
├── main.py
├── mini_git.py
├── check_constraints.py
├── peer_review_check.sh
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

### `main.py`

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

따라서 한 실행 세션 동안 생성한 커밋과 브랜치 정보가 계속 유지됩니다.

---

### `mini_git.py`

Mini Git 저장소의 상태와 명령어 기능을 담당합니다.

주요 역할:

- 저장소 초기화
- 브랜치 생성 및 전환
- 커밋 생성
- commit hash 생성
- 브랜치 HEAD 갱신
- 부모-자식 관계 저장
- 키워드 및 작성자 역색인 갱신
- 커밋 로그 출력
- 날짜 및 작성자 정렬
- 최단 경로 탐색 요청
- 조상 탐색 요청
- 검색 결과 및 로그 출력 형식 생성
- 에러 처리

---

### `models/commit.py`

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

첫 번째 커밋은 부모가 없으므로 빈 리스트를 가집니다.

```python
parents = []
```

일반 커밋은 이전 HEAD를 부모로 가집니다.

```python
parents = ["abc123"]
```

자료구조 자체는 여러 부모를 저장할 수 있으므로 추후 Merge 기능으로 확장할 수 있습니다.

---

### `algorithms/graph.py`

그래프 탐색 알고리즘을 담당합니다.

| 함수 | 역할 |
|---|---|
| `topological_commit_order()` | 부모 커밋 우선 LOG 순서 생성 |
| `_visit_commit_for_log()` | DFS로 부모 커밋을 먼저 방문 |
| `find_shortest_path()` | BFS로 두 커밋 사이의 최단 경로 탐색 |
| `_get_neighbors()` | 현재 커밋의 부모와 자식 이웃 조회 |
| `_find_lexicographically_smallest_path()` | 여러 최단 경로 중 사전순 최소 경로 선택 |
| `find_all_ancestors()` | 특정 커밋의 모든 조상 탐색 |
| `_visit_ancestor()` | 부모 방향 DFS 탐색 |

그래프 알고리즘을 `mini_git.py`와 분리하여 저장소 상태 관리와 탐색 알고리즘이 섞이지 않도록 구성하였습니다.

---

### `algorithms/sorting.py`

Python 표준 정렬 API를 사용하지 않고 직접 구현한 Merge Sort가 포함되어 있습니다.

| 함수 | 역할 |
|---|---|
| `merge_sort()` | 리스트를 절반씩 분할하고 재귀적으로 정렬 |
| `_merge()` | 정렬된 두 리스트를 하나로 병합 |

비교 함수를 인자로 전달하기 때문에 동일한 Merge Sort를 날짜 정렬과 작성자 정렬에 모두 사용할 수 있습니다.

---

### `check_constraints.py`

프로젝트 Python 코드에서 금지된 정렬 API가 실제 실행 코드에 사용되었는지 검사합니다.

검사 대상:

- `sorted()`
- `.sort()`

이 파일은 Python AST를 이용합니다.

따라서 다음과 같이 주석이나 docstring에 작성된 문장은 오류로 인식하지 않습니다.

```python
# sorted()와 list.sort()는 사용하지 않는다.
```

반면 실제 코드에서 다음과 같이 사용하면 탐지합니다.

```python
sorted(items)
items.sort()
```

`.venv`, `.git`, `__pycache__` 디렉터리는 검사 대상에서 제외합니다.

---

### `peer_review_check.sh`

문법 검사, 정렬 API 제한 검사, 자동 테스트를 한 번에 실행하는 셸 스크립트입니다.

실행 순서:

```text
Python 문법 검사
    ↓
금지된 정렬 API 검사
    ↓
기본 명령어 테스트
    ↓
브랜치 테스트
    ↓
검색 테스트
    ↓
에러 처리 테스트
```

모든 검사가 통과하면 마지막에 다음 메시지가 출력됩니다.

```text
ALL AUTOMATED CHECKS PASSED
```

---

### `tests/basic_commands.txt`

다음 기본 기능을 검증합니다.

- INIT
- COMMIT
- BRANCH
- SWITCH
- LOG
- 날짜 정렬
- 작성자 정렬
- 프로그램 종료

---

### `tests/branch_commands.txt`

다음 브랜치 기능을 검증합니다.

- 같은 커밋에서 브랜치 분기
- 브랜치별 HEAD 독립 관리
- 부모 커밋 우선 LOG 출력

---

### `tests/search_commands.txt`

다음 검색 기능을 검증합니다.

- 단일 키워드 검색
- 대소문자를 구분하지 않는 검색
- 여러 키워드 검색
- 검색 결과 없음
- 작성자 검색
- 공백이 포함된 작성자 검색

---

### `tests/error_commands.txt`

다음 에러 상황을 검증합니다.

- INIT 전 명령 실행
- 인자 누락
- 인자 초과
- 중복 브랜치 생성
- 존재하지 않는 브랜치
- 잘못된 정렬 옵션
- 존재하지 않는 커밋
- 지원하지 않는 명령어

---

## 7. 실행 방법

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

프로그램 종료:

```text
exit
```

또는:

```text
quit
```

---

## 8. CLI 명령어 문법

### 명령어 대소문자

명령어는 대소문자를 구분하지 않습니다.

```text
INIT "Alice"
init "Alice"
Init "Alice"
```

모두 동일한 명령으로 처리됩니다.

```python
command = parts[0].lower()
```

---

### 공백이 포함된 문자열

사용자 이름, 커밋 메시지, 검색 키워드에 공백이 포함되면 따옴표로 감쌉니다.

```text
INIT "Alice Kim"
COMMIT "Add login feature"
SEARCH "login feature"
```

`shlex.split()`을 사용하여 따옴표 안의 문자열을 하나의 인자로 처리합니다.

입력:

```text
COMMIT "Add login feature"
```

파싱 결과:

```python
[
    "COMMIT",
    "Add login feature",
]
```

작성자 이름에 공백이 포함된 경우 전체 옵션을 따옴표로 감쌉니다.

```text
SEARCH "--author=Alice Kim"
```

---

### 옵션 형식

```text
SEARCH --author=<name>
LOG --sort-by=date
LOG --sort-by=author
```

예:

```text
SEARCH --author=Alice
```

```text
SEARCH "--author=Alice Kim"
```

---

### 잘못된 따옴표

닫히지 않은 따옴표가 입력되면 다음 메시지를 출력합니다.

```text
Invalid args
```

예:

```text
COMMIT "Add login feature
```

프로그램은 종료되지 않고 다음 명령을 계속 입력받습니다.

---

## 9. 명령어 목록

| 명령어 | 설명 |
|---|---|
| `INIT <user_name>` | 저장소를 초기화하고 main 브랜치를 생성 |
| `BRANCH <branch_name>` | 현재 HEAD를 가리키는 새 브랜치 생성 |
| `SWITCH <branch_name>` | 지정한 브랜치로 전환 |
| `COMMIT <message>` | 현재 브랜치에 새 커밋 생성 |
| `LOG` | 부모 커밋 우선 순서로 로그 출력 |
| `LOG --sort-by=date` | timestamp 기준 로그 정렬 |
| `LOG --sort-by=author` | 작성자 이름 기준 로그 정렬 |
| `PATH <commit1> <commit2>` | 두 커밋 사이의 최단 경로 출력 |
| `ANCESTORS <commit_hash>` | 특정 커밋의 모든 조상 출력 |
| `SEARCH <keyword>` | 메시지 키워드로 커밋 검색 |
| `SEARCH --author=<name>` | 작성자로 커밋 검색 |
| `exit` | 프로그램 종료 |
| `quit` | 프로그램 종료 |

---

## 10. 핵심 자료구조

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

| 변수 | 타입 | 역할 |
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

전체 구조:

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

## 11. 저장소 초기화

명령어:

```text
INIT "Alice"
```

처리 과정:

```text
사용자 이름 확인
    ↓
기존 상태 초기화
    ↓
main 브랜치 생성
    ↓
main HEAD = None
    ↓
current_branch = main
    ↓
current_user = Alice
    ↓
역색인 및 children 초기화
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

---

## 12. 브랜치와 HEAD

브랜치는 전체 커밋 목록을 복사하지 않습니다.

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

현재 HEAD는 다음 구조로 확인합니다.

```text
current_branch
    ↓
branches[current_branch]
    ↓
현재 HEAD commit hash
```

코드:

```python
current_head = self.branches[self.current_branch]
```

---

## 13. 브랜치 생성과 전환

### BRANCH

```text
BRANCH feature
```

새 브랜치는 현재 HEAD를 그대로 가리킵니다.

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

`BRANCH`는 브랜치를 생성하지만 현재 브랜치를 자동으로 변경하지 않습니다.

---

### SWITCH

```text
SWITCH feature
```

현재 브랜치 이름만 변경합니다.

```python
self.current_branch = "feature"
```

존재하지 않는 브랜치를 입력하면 다음을 출력합니다.

```text
Unknown branch: unknown
```

---

## 14. 커밋 생성

명령어:

```text
COMMIT "Add login feature"
```

처리 과정:

```text
저장소 초기화 여부 확인
    ↓
커밋 메시지 확인
    ↓
timestamp 생성
    ↓
현재 HEAD 조회
    ↓
부모 hash 목록 생성
    ↓
고유 commit hash 생성
    ↓
Commit 객체 생성
    ↓
commits에 저장
    ↓
현재 브랜치 HEAD 이동
    ↓
children 갱신
    ↓
keyword_index 갱신
    ↓
author_index 갱신
```

첫 번째 커밋은 부모가 없습니다.

```python
parents = []
```

두 번째 커밋부터는 이전 HEAD가 부모가 됩니다.

```python
parents = ["previous_commit_hash"]
```

커밋 저장:

```python
self.commits[commit_hash] = commit
```

브랜치 HEAD 이동:

```python
self.branches[self.current_branch] = commit_hash
```

---

## 15. 브랜치 분기 예시

명령어:

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

`main` 브랜치에서 새 커밋을 생성해도 `feature` 브랜치의 HEAD는 이동하지 않습니다.

---

## 16. commit hash 생성과 중복 방지

commit hash는 다음 정보를 결합해 생성합니다.

```text
commit_counter
message
author
timestamp
```

코드:

```python
source_text = (
    f"{self.commit_counter}|"
    f"{message}|"
    f"{author}|"
    f"{timestamp.isoformat()}"
)
```

SHA-1 적용:

```python
full_hash = hashlib.sha1(
    source_text.encode("utf-8")
).hexdigest()
```

앞 6자리 사용:

```python
commit_hash = full_hash[:6]
```

6자리 hash는 이론적으로 충돌할 수 있으므로 기존 저장소를 확인합니다.

```python
if commit_hash not in self.commits:
    return commit_hash
```

충돌하면 카운터를 증가시켜 다시 생성합니다.

따라서 한 실행 세션 안에서는 중복 commit hash가 저장되지 않습니다.

---

## 17. 커밋 저장소와 빠른 조회

모든 커밋은 딕셔너리에 저장합니다.

```python
self.commits: dict[str, Commit] = {}
```

구조:

```text
commit hash -> Commit 객체
```

조회:

```python
commit = self.commits[commit_hash]
```

Python 딕셔너리의 평균 조회 시간은 다음과 같습니다.

```text
O(1)
```

커밋을 리스트에만 저장하면 원하는 hash를 찾기 위해 모든 커밋을 확인해야 하므로 O(n)이 필요합니다.

---

## 18. 커밋 그래프와 DAG

DAG는 Directed Acyclic Graph, 즉 방향성 비순환 그래프입니다.

### 방향성

각 커밋은 자신의 부모 커밋을 가리킵니다.

```text
새 커밋 -> 이전 커밋
```

### 비순환

새 커밋은 이미 존재하는 과거 커밋만 부모로 설정합니다.

```text
A 생성
B 생성: 부모 A
C 생성: 부모 B
```

다음과 같은 순환은 생성되지 않습니다.

```text
A -> B -> C -> A
```

### 그래프

브랜치가 분기되면 하나의 선형 구조가 아니라 여러 경로가 만들어집니다.

```text
          B
         /
A
         \
          C
```

따라서 커밋 구조는 방향이 있고 순환이 없는 DAG입니다.

사이클이 발생하면 다음 문제가 생길 수 있습니다.

- 조상과 후손의 관계가 깨짐
- 부모 우선 순서를 결정할 수 없음
- 위상 정렬 불가능
- 탐색이 무한 반복될 가능성
- 과거 방향으로 이력을 추적한다는 의미가 사라짐

---

## 19. 부모-자식 인접 리스트

`Commit` 객체는 부모 hash를 저장합니다.

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

그러나 PATH에서는 부모-자식 연결을 무방향으로 처리해야 합니다.

```text
부모 -> 자식
자식 -> 부모
```

부모에서 자식 방향으로도 빠르게 이동하기 위해 `children` 인접 리스트를 관리합니다.

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

---

## 20. 부모 우선 LOG

일반 Git log는 최신 커밋부터 출력하지만, 본 프로젝트의 `LOG`는 부모 커밋을 자식 커밋보다 먼저 출력합니다.

그래프:

```text
A <- B <- C
```

출력:

```text
A
B
C
```

현재 커밋을 결과에 추가하기 전에 부모를 먼저 DFS로 방문합니다.

```python
for parent_hash in commit.parents:
    _visit_commit_for_log(parent_hash)

result.append(commit_hash)
```

탐색 과정:

```text
visit C
    visit B
        visit A
            add A
        add B
    add C
```

브랜치가 나뉜 경우 자식 커밋끼리의 상대적 순서는 달라질 수 있지만, 부모는 반드시 먼저 출력됩니다.

시간복잡도:

```text
O(V + E)
```

- V: 커밋 수
- E: 부모-자식 연결 수

---

## 21. Merge Sort

정렬 기능에서는 Python 표준 정렬 API를 사용하지 않았습니다.

```python
sorted()
list.sort()
```

대신 Merge Sort를 직접 구현하였습니다.

처리 과정:

```text
리스트를 절반으로 분할
    ↓
왼쪽 절반 재귀 정렬
    ↓
오른쪽 절반 재귀 정렬
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

## 22. 날짜 및 작성자 정렬

날짜 정렬:

```text
LOG --sort-by=date
```

timestamp가 빠른 커밋을 먼저 배치합니다.

```python
return first.timestamp < second.timestamp
```

timestamp가 같으면 hash를 동률 처리 기준으로 사용합니다.

작성자 정렬:

```text
LOG --sort-by=author
```

작성자 이름을 소문자로 변환해 사전순으로 비교합니다.

```python
first_author = first.author.lower()
second_author = second.author.lower()
```

작성자가 같으면 timestamp를 비교하고, timestamp도 같으면 hash를 비교합니다.

비교 함수만 변경하여 동일한 Merge Sort를 재사용합니다.

```python
merge_sort(
    commits,
    comparison_function,
)
```

---

## 23. Merge Sort 복잡도와 안정성

| 경우 | 시간복잡도 |
|---|---:|
| 최선 | O(n log n) |
| 평균 | O(n log n) |
| 최악 | O(n log n) |

추가 공간복잡도:

```text
O(n)
```

비교 결과가 같은 경우 왼쪽 리스트의 원소를 먼저 선택합니다.

```python
if comes_before_or_equal(left_item, right_item):
    result.append(left_item)
```

따라서 같은 비교 값을 가진 원소의 기존 상대적 순서가 유지되며, 안정 정렬입니다.

---

## 24. PATH 최단 경로

명령어:

```text
PATH <commit1> <commit2>
```

부모-자식 연결을 무방향 간선으로 간주하고 BFS로 최단 경로를 탐색합니다.

그래프:

```text
A <- B <- C
```

가능한 이동:

```text
A -> B
B -> A
B -> C
C -> B
```

모든 간선의 비용은 1이므로 BFS가 최소 간선 수 경로를 찾을 수 있습니다.

BFS 큐에는 시작점부터 현재 커밋까지의 전체 경로를 저장합니다.

```python
queue: deque[list[str]] = deque()
queue.append([start_hash])
```

무방향 그래프에서 같은 커밋을 반복 방문하지 않도록 현재 경로에 이미 포함된 커밋은 제외합니다.

```python
if neighbor_hash in current_path:
    continue
```

---

## 25. 사전순 최소 경로

최단 경로가 여러 개라면 각 경로를 문자열로 변환합니다.

```text
hash1->hash2->hash3
```

예:

```text
aaa111->bbb222->ddd444
aaa111->ccc333->ddd444
```

표준 정렬 API를 사용하지 않고 문자열을 직접 비교합니다.

```python
if path_text < smallest_text:
    smallest_path = path
```

경로가 존재하지 않으면 다음을 출력합니다.

```text
No path
```

일반적인 BFS 시간복잡도:

```text
O(V + E)
```

동일한 길이의 최단 경로가 매우 많은 경우에는 여러 경로를 저장하므로 추가 메모리가 사용될 수 있습니다.

---

## 26. ANCESTORS 조상 탐색

명령어:

```text
ANCESTORS <commit_hash>
```

대상 커밋에서 부모 방향으로 도달 가능한 모든 조상을 DFS로 탐색합니다.

그래프:

```text
A <- B <- C
```

입력:

```text
ANCESTORS C
```

결과:

```text
A
B
```

대상 커밋 C 자신은 포함하지 않습니다.

같은 조상이 여러 경로에서 발견되어도 중복 출력되지 않도록 `visited` 집합을 사용합니다.

```python
if commit_hash in visited:
    return
```

시간복잡도:

```text
O(V + E)
```

여기서 V와 E는 도달 가능한 조상 부분 그래프의 커밋과 연결 수입니다.

---

## 27. 역색인

검색 시 모든 커밋을 순회하지 않고 역색인을 사용합니다.

```text
keyword -> commit hash 목록
author -> commit hash 목록
```

역색인은 검색 시점이 아니라 커밋 생성 시점에 갱신합니다.

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

## 28. 키워드 인덱스

커밋 메시지는 소문자로 변환한 뒤 공백 기준으로 분리합니다.

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

같은 메시지 안에서 동일한 단어가 반복되는 경우 같은 hash가 여러 번 저장되지 않도록 `set`을 사용합니다.

```python
added_tokens: set[str] = set()
```

---

## 29. 작성자 인덱스

작성자 이름은 소문자로 정규화합니다.

```python
author_key = commit.author.lower()
```

예:

```text
Alice Kim
```

저장되는 key:

```text
alice kim
```

따라서 다음 검색은 같은 결과를 반환합니다.

```text
SEARCH "--author=Alice Kim"
SEARCH "--author=alice kim"
SEARCH "--author=ALICE KIM"
```

원래 작성자 이름은 `Commit.author`에 보존되므로 출력에는 입력 당시의 형태가 표시됩니다.

---

## 30. 여러 키워드 검색

다음과 같은 검색도 지원합니다.

```text
SEARCH "login feature"
```

검색어를 여러 토큰으로 분리합니다.

```python
query_tokens = keyword.strip().lower().split()
```

각 토큰의 인덱스 목록에 모두 포함된 커밋만 결과로 남깁니다.

```text
login 포함
AND
feature 포함
```

정확히 연속된 문자열을 검색하는 것이 아니라 두 토큰을 모두 가진 커밋을 검색합니다.

---

## 31. 역색인과 순회 검색 비교

모든 커밋을 직접 순회하는 방식:

```python
for commit in self.commits.values():
    if keyword in commit.message:
        ...
```

시간복잡도:

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

검색 결과가 r개라면 일반적인 검색 비용은 다음과 같습니다.

```text
O(1 + r)
```

커밋 생성 시에는 메시지 토큰 수 k에 비례하는 인덱스 갱신 비용이 필요합니다.

```text
O(k)
```

즉 검색을 빠르게 하기 위해 저장 시점에 미리 추가 작업을 수행하는 구조입니다.

---

## 32. 에러 처리

| 상황 | 출력 |
|---|---|
| INIT 전 명령 실행 | `Repository not initialized` |
| 잘못된 인자 | `Invalid args` |
| 존재하지 않는 브랜치 | `Unknown branch: <name>` |
| 중복 브랜치 | `Branch already exists: <name>` |
| 존재하지 않는 커밋 | `Unknown commit: <hash>` |
| 지원하지 않는 명령어 | `Unknown command: <command>` |
| 커밋이 없는 LOG | `No commits` |
| 조상이 없는 커밋 | `No ancestors` |
| 연결 경로 없음 | `No path` |

---

## 33. 시간복잡도 요약

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

```text
k = 커밋 메시지 토큰 수
r = 검색 결과 수
V = 커밋 수
E = 부모-자식 연결 수
n = 정렬 대상 커밋 수
b = 브랜치 수
```

---

## 34. 자동 테스트

개별 테스트 실행:

```bash
python main.py < tests/basic_commands.txt
```

```bash
python main.py < tests/branch_commands.txt
```

```bash
python main.py < tests/search_commands.txt
```

```bash
python main.py < tests/error_commands.txt
```

전체 테스트 실행:

```bash
python main.py < tests/basic_commands.txt
python main.py < tests/branch_commands.txt
python main.py < tests/search_commands.txt
python main.py < tests/error_commands.txt
```

테스트 파일 마지막에는 `quit` 명령이 포함되어 있으므로 각 테스트가 자동으로 종료됩니다.

리다이렉션 테스트는 매우 빠르게 실행되기 때문에 여러 커밋의 timestamp가 같은 초로 출력될 수 있습니다.

timestamp가 같으면 hash를 동률 처리 기준으로 사용합니다.

---

## 35. PATH와 ANCESTORS 수동 테스트

commit hash는 실행할 때마다 생성되므로 실제 출력된 hash를 사용합니다.

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

Commit A와 Commit B가 출력되어야 합니다.

첫 번째 커밋 테스트:

```text
ANCESTORS aa1111
```

예상 결과:

```text
No ancestors
```

실제 hash는 실행할 때마다 달라질 수 있습니다.

---

## 36. 문법 검사

다음 명령으로 모든 Python 파일의 문법을 확인합니다.

```bash
python -m py_compile \
main.py \
mini_git.py \
check_constraints.py \
models/commit.py \
algorithms/graph.py \
algorithms/sorting.py
```

오류가 없으면 아무 내용도 출력되지 않습니다.

---

## 37. 금지된 정렬 API 검사

실행:

```bash
python check_constraints.py
```

정상 결과 예:

```text
Mini Git constraint check
Checked Python files: 5

PASS: No forbidden sorting API usage found.
- sorted() not used
- list.sort() / .sort() not used
- .venv, .git, and __pycache__ excluded
```

검사 파일 수는 프로젝트의 Python 파일 수에 따라 달라질 수 있습니다.

이 검사는 Python AST를 이용하므로 주석과 docstring에 작성된 `sorted()` 문장은 무시하고 실제 함수 호출만 검사합니다.

---

## 38. 전체 검증 스크립트

최초 한 번 실행 권한을 부여합니다.

```bash
chmod +x peer_review_check.sh
```

이후 다음 명령 하나로 전체 검증을 실행할 수 있습니다.

```bash
./peer_review_check.sh
```

검증 항목:

```text
1. Python 문법
2. 금지된 정렬 API
3. 기본 명령어
4. 브랜치 기능
5. 검색 기능
6. 에러 처리
```

모든 검사가 완료되면 다음 메시지가 출력됩니다.

```text
ALL AUTOMATED CHECKS PASSED
```

---

## 39. 실행 예시

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

## 40. 실제 Git과 Mini Git의 차이

| 항목 | 실제 Git | Mini Git |
|---|---|---|
| 파일 내용 | Blob 객체로 저장 | 저장하지 않음 |
| 디렉터리 | Tree 객체로 저장 | 저장하지 않음 |
| commit hash | 객체 내용 전체 기반 | counter, message, author, timestamp 기반 |
| hash 길이 | 전체 hash 사용 | 앞 6자리 사용 |
| 데이터 저장 | `.git` 디렉터리에 영속 저장 | 메모리에서만 동작 |
| 브랜치 | ref가 commit hash 저장 | 딕셔너리에 HEAD hash 저장 |
| HEAD | ref 또는 commit을 가리킴 | 현재 브랜치 이름 저장 |
| Merge commit | 여러 부모 지원 | 자료구조만 지원, 명령 미구현 |
| Diff | 파일 차이 비교 | 미구현 |
| 네트워크 | push, pull, fetch | 미구현 |

---

## 41. 핵심 학습 내용

이 프로젝트를 통해 다음 내용을 직접 구현하고 확인하였습니다.

### 커밋 그래프

커밋은 단순한 최신순 목록이 아니라 부모 연결을 가진 DAG 구조입니다.

### 브랜치

브랜치는 전체 커밋 이력을 복사하지 않고 특정 commit hash 하나를 가리킵니다.

### HEAD

현재 선택된 브랜치 이름과 해당 브랜치가 가리키는 commit hash를 통해 관리합니다.

### DFS

LOG의 부모 우선 출력과 ANCESTORS의 조상 탐색에 사용하였습니다.

### BFS

가중치가 없는 커밋 그래프에서 최소 간선 수 경로를 찾기 위해 사용하였습니다.

### Merge Sort

표준 정렬 API 없이 최선, 평균, 최악 모두 O(n log n)인 안정 정렬을 직접 구현하였습니다.

### 비교 함수

정렬 알고리즘은 유지하고 비교 함수만 변경하여 날짜와 작성자 정렬에 재사용하였습니다.

### 역색인

검색할 때 모든 커밋을 순회하지 않고 키워드 또는 작성자에서 commit hash 목록을 바로 조회하도록 구현하였습니다.

### 자동 검증

AST 기반 검사와 셸 스크립트를 이용하여 문법, 제약 사항, 주요 기능 테스트를 한 번에 확인할 수 있도록 구성하였습니다.