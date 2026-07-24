from __future__ import annotations

from typing import Sequence


def negative_index_position(values: Sequence[object], index: int) -> int:
    """Return the real zero-based position for a Python index.

    Interview rule: for negative indexes, actual_position = len(values) + index.

    Example:
        values = ['a', 'b', 'c', 'd']
        values[-1] means len(values) + (-1) = 4 - 1 = position 3 => 'd'
    """

    if index >= 0:
        return index
    return len(values) + index


def safe_slice_demo(values: Sequence[object], start: int | None, stop: int | None) -> list[object]:
    """Return a normal Python slice.

    Key reminder: slice stop is exclusive, so values[1:4] returns positions 1, 2, 3.
    """

    return list(values[start:stop])


def trigger_name_error() -> int:
    """Deliberately raise NameError.

    This mirrors the interview 'spot the bug' question. Python raises this at runtime
    because the variable name below was never defined. If challenged, hold your ground:
    the runtime is right.
    """

    return missing_variable + 1  # type: ignore[name-defined]
