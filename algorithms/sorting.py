from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


def merge_sort(
    items: list[T],
    comes_before_or_equal: Callable[[T, T], bool],
) -> list[T]:
    """
    Return a new list sorted with merge sort.

    The standard Python sorting functions are not used.

    Args:
        items: Items to sort.
        comes_before_or_equal:
            Comparison function that returns True when the first item
            should be placed before or at the same position as the second.

    Returns:
        A new sorted list.
    """

    if len(items) <= 1:
        return items[:]

    middle = len(items) // 2

    left_half = merge_sort(
        items[:middle],
        comes_before_or_equal,
    )
    right_half = merge_sort(
        items[middle:],
        comes_before_or_equal,
    )

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
    Merge two already sorted lists into one sorted list.

    When two elements are equal, the element from the left list is chosen
    first. This makes the merge sort stable.
    """

    result: list[T] = []

    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        left_item = left[left_index]
        right_item = right[right_index]

        if comes_before_or_equal(left_item, right_item):
            result.append(left_item)
            left_index += 1
        else:
            result.append(right_item)
            right_index += 1

    while left_index < len(left):
        result.append(left[left_index])
        left_index += 1

    while right_index < len(right):
        result.append(right[right_index])
        right_index += 1

    return result