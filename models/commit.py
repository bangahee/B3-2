from __future__ import annotations

# dataclass는 데이터 저장이 중심인 클래스를 간단하게 만들기 위해 사용한다.
#
# 일반 클래스로 작성하면 __init__() 같은 메서드를 직접 만들어야 하지만,
# @dataclass를 사용하면 필드 선언만으로 필요한 기본 메서드가 자동 생성된다.
from dataclasses import dataclass

# datetime은 커밋이 생성된 날짜와 시간을 저장하기 위해 사용한다.
from datetime import datetime


@dataclass
class Commit:
    """
    Mini Git의 커밋 그래프에서 하나의 커밋 노드를 표현한다.

    이 클래스는 커밋의 핵심 메타데이터를 저장한다.

    Attributes:
        hash:
            커밋을 구분하기 위한 고유 식별자이다.

        message:
            사용자가 작성한 커밋 메시지이다.

        author:
            커밋을 생성한 작성자의 이름이다.

        timestamp:
            커밋이 생성된 날짜와 시간이다.

        parents:
            부모 커밋들의 hash를 저장하는 리스트이다.

            첫 번째 커밋은 부모가 없기 때문에 빈 리스트를 가진다.

            일반 커밋은 현재 HEAD를 부모로 가지므로
            보통 하나의 부모 hash를 가진다.

            추후 Merge 기능을 구현하면
            두 개 이상의 부모 hash를 저장할 수도 있다.
    """

    # 커밋을 빠르게 조회하고 서로 구분하기 위한 고유 hash이다.
    hash: str

    # 사용자가 COMMIT 명령으로 입력한 커밋 메시지이다.
    message: str

    # 이 커밋을 생성한 사용자의 이름이다.
    author: str

    # 커밋이 생성된 시각을 저장한다.
    #
    # LOG --sort-by=date에서 날짜 정렬 기준으로 사용된다.
    timestamp: datetime

    # 부모 커밋들의 hash를 저장한다.
    #
    # 실제 Commit 객체를 직접 저장하지 않고 hash만 저장하는 이유는
    # 커밋 간 연결을 단순하게 유지하고,
    # commits 딕셔너리에서 hash로 빠르게 조회하기 위해서이다.
    #
    # 예:
    # 첫 번째 커밋:
    # parents = []
    #
    # 일반 커밋:
    # parents = ["abc123"]
    #
    # Merge 커밋으로 확장할 경우:
    # parents = ["abc123", "def456"]
    parents: list[str]