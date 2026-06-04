"""Chapter 3 finite group scaffolding.

These signatures are intentionally exercise-shaped: fill in the bodies by translating the
Chapter 3 group and subgroup definitions into finite brute-force checks.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Hashable, Iterable, Sequence
from dataclasses import dataclass
from itertools import product
from math import gcd
from typing import Any, Self

type BinaryOperation[ElementT: Hashable] = Callable[[ElementT, ElementT], ElementT]
type CayleyTable[ElementT: Hashable] = dict[tuple[ElementT, ElementT], ElementT]


@dataclass(frozen=True)
class FiniteGroupCandidate[ElementT: Hashable]:
    """A finite set with a proposed binary operation."""

    elements: frozenset[ElementT]
    operation: BinaryOperation[ElementT]

    @classmethod
    def from_elements(
        cls,
        elements: Iterable[ElementT],
        operation: BinaryOperation[ElementT],
    ) -> Self:
        """Build a candidate from any iterable of hashable elements."""
        element_set = frozenset(elements)
        if not element_set:
            msg = "a group candidate must have at least one element"
            raise ValueError(msg)
        return cls(element_set, operation)

    def combine(self, left: ElementT, right: ElementT) -> ElementT:
        """Apply the candidate operation."""
        return self.operation(left, right)


@dataclass(frozen=True)
class CandidateExample[ElementT: Hashable]:
    """A named finite group candidate for running Chapter 3 checks."""

    name: str
    candidate: FiniteGroupCandidate[ElementT]


type CandidateRunner = Callable[[FiniteGroupCandidate[Any]], object]


def zmod_elements(n: int) -> frozenset[int]:
    """Return the elements of Z_n as canonical representatives ``0`` through ``n - 1``."""
    if n <= 0:
        msg = "n must be positive"
        raise ValueError(msg)
    return frozenset(range(n))


def units_mod_elements(n: int) -> frozenset[int]:
    """Return the multiplicative units modulo ``n``."""
    if n <= 1:
        msg = "n must be greater than 1"
        raise ValueError(msg)
    return frozenset(k for k in range(n) if gcd(k, n) == 1)


def addition_mod(n: int) -> BinaryOperation[int]:
    """Return addition modulo ``n``."""
    if n <= 0:
        msg = "n must be positive"
        raise ValueError(msg)

    def add(left: int, right: int) -> int:
        return (left + right) % n

    return add


def multiplication_mod(n: int) -> BinaryOperation[int]:
    """Return multiplication modulo ``n``."""
    if n <= 0:
        msg = "n must be positive"
        raise ValueError(msg)

    def multiply(left: int, right: int) -> int:
        return (left * right) % n

    return multiply


def zn_addition_candidate(n: int) -> CandidateExample[int]:
    """Return ``Z_n`` as a candidate under addition modulo ``n``."""
    return CandidateExample(
        name=f"Z_{n} under addition",
        candidate=FiniteGroupCandidate.from_elements(zmod_elements(n), addition_mod(n)),
    )


def zn_multiplication_candidate(n: int) -> CandidateExample[int]:
    """Return ``Z_n`` as a candidate under multiplication modulo ``n``."""
    return CandidateExample(
        name=f"Z_{n} under multiplication",
        candidate=FiniteGroupCandidate.from_elements(zmod_elements(n), multiplication_mod(n)),
    )


def units_mod_candidate(n: int) -> CandidateExample[int]:
    """Return ``U(n)`` as a candidate under multiplication modulo ``n``."""
    return CandidateExample(
        name=f"U({n}) under multiplication",
        candidate=FiniteGroupCandidate.from_elements(units_mod_elements(n), multiplication_mod(n)),
    )


def z2_power_candidate(dimension: int) -> CandidateExample[tuple[int, ...]]:
    """Return ``Z_2^dimension`` under componentwise addition modulo 2."""
    if dimension <= 0:
        msg = "dimension must be positive"
        raise ValueError(msg)

    elements = frozenset(tuple(bits) for bits in product((0, 1), repeat=dimension))

    def add(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
        return tuple((a + b) % 2 for a, b in zip(left, right, strict=True))

    return CandidateExample(
        name=f"Z_2^{dimension} under componentwise addition",
        candidate=FiniteGroupCandidate.from_elements(elements, add),
    )


def dihedral_candidate(sides: int) -> CandidateExample[tuple[int, int]]:
    """Return the dihedral group ``D_sides`` using pairs ``(rotation, reflection)``."""
    if sides < 3:
        msg = "a dihedral symmetry group needs at least 3 sides"
        raise ValueError(msg)

    elements = frozenset(
        (rotation, reflection)
        for rotation in range(sides)
        for reflection in (0, 1)
    )

    def compose(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
        left_rotation, left_reflection = left
        right_rotation, right_reflection = right
        reflected_sign = -1 if left_reflection else 1
        return (
            (left_rotation + reflected_sign * right_rotation) % sides,
            (left_reflection + right_reflection) % 2,
        )

    return CandidateExample(
        name=f"D_{sides}, symmetries of a regular {sides}-gon",
        candidate=FiniteGroupCandidate.from_elements(elements, compose),
    )


def candidate_examples() -> dict[str, CandidateExample[Any]]:
    """Return a small registry of candidates useful for Chapter 3 experiments."""
    return {
        "z4-add": zn_addition_candidate(4),
        "z8-add": zn_addition_candidate(8),
        "z4-mul": zn_multiplication_candidate(4),
        "u12": units_mod_candidate(12),
        "z2-3": z2_power_candidate(3),
        "d4": dihedral_candidate(4),
    }


def cayley_table[ElementT: Hashable](
    candidate: FiniteGroupCandidate[ElementT],
) -> CayleyTable[ElementT]:
    """Return the full operation table keyed by ordered element pairs."""
    table: CayleyTable[ElementT] = {}
    for e1 in candidate.elements:
        for e2 in candidate.elements:
            table[(e1, e2)] = candidate.combine(e1, e2)
    return table


def ordered_elements[ElementT: Hashable](
    candidate: FiniteGroupCandidate[ElementT],
) -> tuple[ElementT, ...]:
    """Return elements in a deterministic display order."""
    return tuple(sorted(candidate.elements, key=repr))


def format_cayley_table[ElementT: Hashable](
    candidate: FiniteGroupCandidate[ElementT],
    table: CayleyTable[ElementT] | None = None,
) -> str:
    """Format a Cayley table for terminal output."""
    elements = ordered_elements(candidate)
    resolved_table = cayley_table(candidate) if table is None else table

    headings = [repr(element) for element in elements]
    rows = [
        [repr(row), *(repr(resolved_table[(row, column)]) for column in elements)]
        for row in elements
    ]
    width = max(
        len("*"),
        *(len(cell) for cell in headings),
        *(len(cell) for row in rows for cell in row),
    )

    lines = [" ".join(("*".rjust(width), *(heading.rjust(width) for heading in headings)))]
    lines.extend(" ".join(cell.rjust(width) for cell in row) for row in rows)
    return "\n".join(lines)


def is_closed[ElementT: Hashable](candidate: FiniteGroupCandidate[ElementT]) -> bool:
    """Check whether every product of two candidate elements is still in the set."""
    for e1 in candidate.elements:
        for e2 in candidate.elements:
            g = candidate.combine(e1, e2)
            if g not in candidate.elements:
                return False
    return True


def identity[ElementT: Hashable](
    candidate: FiniteGroupCandidate[ElementT],
) -> ElementT | None:
    """Return the two-sided identity element, or ``None`` if no identity exists."""
    e = None
    for g in candidate.elements:
        if all(h == candidate.combine(g, h) == candidate.combine(h, g) for h in candidate.elements):
            if e is None:
                e = g
            else:
                # Two distinct identities found
                return None
    return e


def inverse_of[ElementT: Hashable](
    candidate: FiniteGroupCandidate[ElementT],
    element: ElementT,
    identity_element: ElementT,
) -> ElementT | None:
    """Return a two-sided inverse for ``element`` relative to a known identity."""
    inv = None
    for g in candidate.elements:
        if identity_element == candidate.combine(element, g) == candidate.combine(g, element):
            if inv is None:
                inv = g
            else:
                # duplicate inverse found
                return None
    return inv


def has_inverses[ElementT: Hashable](
    candidate: FiniteGroupCandidate[ElementT],
    identity_element: ElementT,
) -> bool:
    """Check whether every element has a unique two-sided inverse."""
    return all(inverse_of(candidate, g, identity_element) is not None for g in candidate.elements)


def is_associative[ElementT: Hashable](candidate: FiniteGroupCandidate[ElementT]) -> bool:
    """Check associativity over all triples of elements."""
    op = candidate.combine
    for a in candidate.elements:
        for b in candidate.elements:
            for c in candidate.elements:
                if op(op(a, b), c) != op(a, op(b, c)):
                    return False
    return True


def is_group[ElementT: Hashable](candidate: FiniteGroupCandidate[ElementT]) -> bool:
    """Check the Chapter 3 group axioms for a finite candidate."""
    ident = identity(candidate)
    return (
        is_associative(candidate) and
        ident is not None and
        has_inverses(candidate, ident) and
        is_closed(candidate)
    )


def is_abelian[ElementT: Hashable](candidate: FiniteGroupCandidate[ElementT]) -> bool:
    """Check whether every pair of elements commutes."""
    for a in candidate.elements:
        for b in candidate.elements:
            if candidate.combine(a, b) != candidate.combine(b, a):
                return False
    return True


def is_subgroup[ElementT: Hashable](
    group: FiniteGroupCandidate[ElementT],
    subset: Iterable[ElementT],
) -> bool:
    """Check the Chapter 3 subgroup test for a proposed subset."""
    e = identity(group)
    if e is None:
        return False
    if not subset:
        # empty group
        return False
    for h in subset:
        if h not in group.elements:
            return False
        h_inv = inverse_of(group, h, e)
        if h_inv is None:
            return False
        for g in subset:
            if group.combine(g, h_inv) not in subset:
                return False
    return True


def candidate_runners() -> dict[str, CandidateRunner]:
    """Return method dispatchers for the command-line demo."""
    return {
        "cayley-table": format_cayley_table,
        "closed": is_closed,
        "identity": identity,
        "associative": is_associative,
        "group": is_group,
        "abelian": is_abelian,
    }


def run_candidate_method(method_name: str, candidate: FiniteGroupCandidate[Any]) -> object:
    """Run one named method against a candidate."""
    runners = candidate_runners()
    try:
        runner = runners[method_name]
    except KeyError as exc:
        valid = ", ".join(sorted(runners))
        msg = f"unknown method {method_name!r}; choose one of: {valid}"
        raise ValueError(msg) from exc
    return runner(candidate)


def main(argv: Sequence[str] | None = None) -> None:
    """Run a Chapter 3 candidate against one of the checker methods."""
    examples = candidate_examples()
    runners = candidate_runners()

    parser = argparse.ArgumentParser(description="Run Chapter 3 finite-group experiments.")
    parser.add_argument(
        "method",
        nargs="?",
        choices=sorted(runners),
        default="cayley-table",
    )
    parser.add_argument(
        "candidate",
        nargs="?",
        choices=sorted(examples),
        default="z8-add",
    )
    parser.add_argument(
        "--all-candidates",
        action="store_true",
        help="run the selected method for every built-in candidate",
    )
    args = parser.parse_args(argv)

    selected = examples.values() if args.all_candidates else [examples[args.candidate]]
    for example in selected:
        print(example.name)
        try:
            print(run_candidate_method(args.method, example.candidate))
        except NotImplementedError as exc:
            print(exc)
        print()


if __name__ == "__main__":
    main()
