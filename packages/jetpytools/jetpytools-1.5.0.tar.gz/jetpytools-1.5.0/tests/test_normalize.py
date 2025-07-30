from __future__ import annotations
import sys

import pytest

from jetpytools import CustomOverflowError, normalize_ranges


if sys.version_info < (3, 11):
    ExceptionGroup = Exception


def assert_excinfo_group_contains(
    excinfo: pytest.ExceptionInfo, exception: type[Exception]  # type: ignore
) -> None:
    if sys.version_info < (3, 11):
        assert isinstance(excinfo.value, Exception)
    else:
        assert excinfo.group_contains(exception)


def test_normalize_ranges() -> None:
    # Inclusive ranges
    assert normalize_ranges((None, None), length=1000, exclusive=False) == [(0, 999)]
    assert normalize_ranges((24, -24), length=1000, exclusive=False) == [(24, 975)]
    assert normalize_ranges((-100, 950), length=1000, exclusive=False) == [(900, 950)]
    assert normalize_ranges([(24, 100), (80, 150)], length=1000, exclusive=False) == [(24, 150)]
    assert normalize_ranges([500], length=1000, exclusive=False) == [(500, 500)]

    # Exclusive ranges
    assert normalize_ranges((None, None), length=1000, exclusive=True) == [(0, 1000)]
    assert normalize_ranges((24, -24), length=1000, exclusive=True) == [(24, 976)]
    assert normalize_ranges((-100, 950), length=1000, exclusive=True) == [(900, 950)]
    assert normalize_ranges([(24, 100), (80, 150)], length=1000, exclusive=True) == [(24, 150)]
    assert normalize_ranges([500], length=1000, exclusive=True) == [(500, 501)]

    # Overflow
    with pytest.raises(ExceptionGroup) as excinfo:
        normalize_ranges((500, 1500), length=1000)
    assert_excinfo_group_contains(excinfo, CustomOverflowError)

    with pytest.raises(ExceptionGroup) as excinfo:
        normalize_ranges((-2000, 500), length=1000)
    assert_excinfo_group_contains(excinfo, CustomOverflowError)

    with pytest.raises(ExceptionGroup) as excinfo:
        normalize_ranges((-2000, 2000), length=1000)
    assert_excinfo_group_contains(excinfo, CustomOverflowError)

    assert normalize_ranges((500, 1500), length=1000, exclusive=False, strict=False) == [(500, 999)]
    assert normalize_ranges((500, 1500), length=1000, exclusive=True, strict=False) == [(500, 1000)]

    assert normalize_ranges((-1500, 500), length=1000, exclusive=False, strict=False) == [(0, 500)]
    assert normalize_ranges((-1500, 500), length=1000, exclusive=True, strict=False) == [(0, 500)]

    assert normalize_ranges((-2000, 2000), length=1000, exclusive=False, strict=False) == [(0, 999)]
    assert normalize_ranges((-2000, 2000), length=1000, exclusive=True, strict=False) == [(0, 1000)]

    assert normalize_ranges((0, 0), length=1000, exclusive=False, strict=True) == [(0, 0)]

    with pytest.raises(ExceptionGroup) as excinfo:
        normalize_ranges((0, 0), length=1000, exclusive=True, strict=True)
    assert_excinfo_group_contains(excinfo, CustomOverflowError)
