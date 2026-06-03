from __future__ import annotations

from exercises.ch02 import extended_gcd, gcd
from hypothesis import given
from hypothesis import strategies as st


@given(st.integers(), st.integers())
def test_gcd_is_nonnegative_and_divides_inputs(a: int, b: int) -> None:
    result = gcd(a, b)

    assert result >= 0
    if result == 0:
        assert a == 0 and b == 0
    else:
        assert a % result == 0
        assert b % result == 0


@given(st.integers(), st.integers())
def test_extended_gcd_bezout_identity(a: int, b: int) -> None:
    g, x, y = extended_gcd(a, b)

    assert g == gcd(a, b)
    assert a * x + b * y == g
