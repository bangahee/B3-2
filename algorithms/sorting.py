from __future__ import annotations

# Callable은 비교 함수의 자료형을 표현하기 위해 사용한다.
#
# 비교 함수는 두 값을 입력받고,
# 첫 번째 값이 두 번째 값보다 앞에 오거나 같은 위치에 와야 하면
# True를 반환한다.
from collections.abc import Callable

# TypeVar는 이 Merge Sort가 특정 자료형에만 묶이지 않고
# 여러 자료형을 정렬할 수 있도록 하기 위해 사용한다.
from typing import TypeVar


# T는 임의의 자료형을 의미하는 제네릭 타입이다.
#
# 예를 들어 T는 다음과 같은 자료형이 될 수 있다.
#
# - Commit
# - int
# - str
#
# 이 프로젝트에서는 주로 Commit 객체를 정렬할 때 사용한다.
T = TypeVar("T")


def merge_sort(
    items: list[T],
    comes_before_or_equal: Callable[[T, T], bool],
) -> list[T]:
    """
    Merge Sort를 사용하여 정렬된 새 리스트를 반환한다.

    Python의 표준 정렬 함수인 sorted()와 list.sort()는 사용하지 않는다.

    Args:
        items:
            정렬할 원소들이 들어 있는 리스트이다.

        comes_before_or_equal:
            두 원소를 비교하는 함수이다.

            첫 번째 원소가 두 번째 원소보다 앞에 오거나
            같은 위치에 와야 하면 True를 반환한다.

    Returns:
        정렬된 새로운 리스트를 반환한다.

    Time complexity:
        최선: O(n log n)
        평균: O(n log n)
        최악: O(n log n)

    Space complexity:
        O(n)
    """

    # 원소가 0개 또는 1개인 리스트는 이미 정렬된 상태이다.
    #
    # items 자체를 반환하지 않고 items[:]를 사용하여
    # 원본과는 별개의 새 리스트를 반환한다.
    if len(items) <= 1:
        return items[:]

    # 리스트를 왼쪽과 오른쪽으로 나누기 위해 중간 위치를 계산한다.
    middle = len(items) // 2

    # 왼쪽 절반을 재귀적으로 정렬한다.
    #
    # 예:
    # [D, B, A, C]
    #
    # 왼쪽 절반:
    # [D, B]
    left_half = merge_sort(
        items[:middle],
        comes_before_or_equal,
    )

    # 오른쪽 절반을 재귀적으로 정렬한다.
    #
    # 예:
    # [D, B, A, C]
    #
    # 오른쪽 절반:
    # [A, C]
    right_half = merge_sort(
        items[middle:],
        comes_before_or_equal,
    )

    # 각각 정렬된 왼쪽 리스트와 오른쪽 리스트를
    # 하나의 정렬된 리스트로 병합한다.
    return _merge(
        left_half,
        right_half,
        comes_before_or_equal,
    )


def _merge(
    left: list[T],
    right: list[T],
    comes_before_or_equal: Callable[[T, T], bool],
) -> list[T]:
    """
    이미 정렬된 두 리스트를 하나의 정렬된 리스트로 병합한다.

    두 원소의 비교 결과가 같으면 왼쪽 리스트의 원소를 먼저 선택한다.
    따라서 이 Merge Sort는 안정 정렬이다.

    Args:
        left:
            이미 정렬된 왼쪽 리스트이다.

        right:
            이미 정렬된 오른쪽 리스트이다.

        comes_before_or_equal:
            두 원소 중 어떤 원소가 먼저 와야 하는지 판단하는 비교 함수이다.

    Returns:
        left와 right의 모든 원소가 정렬된 새로운 리스트를 반환한다.
    """

    # 왼쪽 리스트와 오른쪽 리스트를 합친 최종 결과를 저장한다.
    result: list[T] = []

    # 왼쪽 리스트에서 현재 비교 중인 위치를 나타낸다.
    left_index = 0

    # 오른쪽 리스트에서 현재 비교 중인 위치를 나타낸다.
    right_index = 0

    # 왼쪽과 오른쪽 리스트에 비교할 원소가 모두 남아 있는 동안 반복한다.
    while left_index < len(left) and right_index < len(right):
        # 왼쪽 리스트의 현재 원소를 가져온다.
        left_item = left[left_index]

        # 오른쪽 리스트의 현재 원소를 가져온다.
        right_item = right[right_index]

        # 전달받은 비교 함수를 이용해
        # 왼쪽 원소와 오른쪽 원소 중 어떤 원소가 먼저 와야 하는지 판단한다.
        #
        # 같은 Merge Sort를 다음과 같은 여러 정렬 기준에 사용할 수 있다.
        #
        # - timestamp 기준
        # - author 기준
        #
        # 두 값이 같은 경우에는 comes_before_or_equal이 True를 반환하도록 하여
        # 왼쪽 원소가 먼저 선택되도록 한다.
        #
        # 왼쪽 원소는 원래 입력에서도 오른쪽 원소보다 앞에 있었기 때문에
        # 같은 값의 기존 상대적 순서가 유지된다.
        #
        # 따라서 이 정렬은 안정 정렬이다.
        if comes_before_or_equal(left_item, right_item):
            result.append(left_item)
            left_index += 1
        else:
            result.append(right_item)
            right_index += 1

    # 오른쪽 리스트의 원소를 먼저 모두 사용한 경우,
    # 왼쪽 리스트에 남아 있는 원소들을 결과에 추가한다.
    #
    # 왼쪽 리스트 자체는 이미 정렬되어 있으므로
    # 남은 원소들을 순서대로 추가하면 된다.
    while left_index < len(left):
        result.append(left[left_index])
        left_index += 1

    # 왼쪽 리스트의 원소를 먼저 모두 사용한 경우,
    # 오른쪽 리스트에 남아 있는 원소들을 결과에 추가한다.
    #
    # 오른쪽 리스트 자체도 이미 정렬되어 있다.
    while right_index < len(right):
        result.append(right[right_index])
        right_index += 1

    # 완성된 정렬 결과를 반환한다.
    return result