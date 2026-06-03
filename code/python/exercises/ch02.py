"""Chapter 2: integer algorithms."""

from __future__ import annotations


def gcd(a: int, b: int) -> int:
    """Return the nonnegative greatest common divisor of two integers."""
    x, y = abs(a), abs(b)
    while y:
        x, y = y, x % y
    return x


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return ``(g, x, y)`` with ``g = gcd(a, b)`` and ``a*x + b*y = g``."""
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    x = old_s if a >= 0 else -old_s
    y = old_t if b >= 0 else -old_t
    return old_r, x, y


def main() -> None:
    examples = [(252, 198), (101, 23), (-84, 30)]

    for a, b in examples:
        g, x, y = extended_gcd(a, b)
        print(f"gcd({a}, {b}) = {g}; Bezout coefficients: x={x}, y={y}")
        print(f"  check: {a}*{x} + {b}*{y} = {a * x + b * y}")


if __name__ == "__main__":
    main()

