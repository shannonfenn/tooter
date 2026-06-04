from __future__ import annotations

from collections.abc import Callable

import exercises.ch03_groups as ch03
import pytest
from exercises.ch03_groups import (
    FiniteGroupCandidate,
    candidate_examples,
    cayley_table,
    dihedral_candidate,
    format_cayley_table,
    has_inverses,
    identity,
    inverse_of,
    is_abelian,
    is_associative,
    is_closed,
    is_group,
    is_subgroup,
    units_mod_candidate,
    z2_power_candidate,
    zn_addition_candidate,
    zn_multiplication_candidate,
)


def run_or_skip[ResultT](fn: Callable[[], ResultT]) -> ResultT:
    try:
        return fn()
    except NotImplementedError as exc:
        pytest.skip(str(exc))


def not_closed_candidate() -> FiniteGroupCandidate[int]:
    return FiniteGroupCandidate.from_elements({0, 1}, lambda left, right: left + right)


def no_identity_candidate() -> FiniteGroupCandidate[int]:
    return FiniteGroupCandidate.from_elements({0, 1}, lambda _left, _right: 0)


def left_identity_only_candidate() -> FiniteGroupCandidate[int]:
    return FiniteGroupCandidate.from_elements({0, 1}, lambda _left, right: right)


def nonassociative_candidate() -> FiniteGroupCandidate[int]:
    def nand(left: int, right: int) -> int:
        return 1 - (left & right)

    return FiniteGroupCandidate.from_elements({0, 1}, nand)


def multiple_inverse_candidate() -> FiniteGroupCandidate[str]:
    elements = {"e", "x", "a", "b"}
    table = {
        ("e", "e"): "e",
        ("e", "x"): "x",
        ("e", "a"): "a",
        ("e", "b"): "b",
        ("x", "e"): "x",
        ("a", "e"): "a",
        ("b", "e"): "b",
        ("x", "a"): "e",
        ("a", "x"): "e",
        ("x", "b"): "e",
        ("b", "x"): "e",
    }

    def op(left: str, right: str) -> str:
        return table.get((left, right), "e")

    return FiniteGroupCandidate.from_elements(elements, op)


def test_cayley_table_contains_every_ordered_pair() -> None:
    candidate = zn_addition_candidate(2).candidate

    table = cayley_table(candidate)

    assert table == {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    }


def test_candidate_examples_include_chapter_3_groups() -> None:
    examples = candidate_examples()

    assert {"z4-add", "z8-add", "z4-mul", "u12", "z2-3", "d4"}.issubset(examples)


def test_format_cayley_table_for_z2_addition() -> None:
    candidate = zn_addition_candidate(2).candidate

    assert format_cayley_table(candidate) == "\n".join(
        [
            "* 0 1",
            "0 0 1",
            "1 1 0",
        ]
    )


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (zn_addition_candidate(4).candidate, True),
        (zn_multiplication_candidate(4).candidate, True),
        (not_closed_candidate(), False),
    ],
)
def test_is_closed(candidate: FiniteGroupCandidate[int], expected: bool) -> None:
    assert run_or_skip(lambda: is_closed(candidate)) is expected


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (zn_addition_candidate(4).candidate, 0),
        (units_mod_candidate(12).candidate, 1),
        (no_identity_candidate(), None),
        (left_identity_only_candidate(), None),
    ],
)
def test_identity(candidate: FiniteGroupCandidate[int], expected: int | None) -> None:
    assert run_or_skip(lambda: identity(candidate)) == expected


@pytest.mark.parametrize(
    ("candidate", "element", "identity_element", "expected"),
    [
        (zn_addition_candidate(4).candidate, 1, 0, 3),
        (zn_addition_candidate(4).candidate, 2, 0, 2),
        (units_mod_candidate(12).candidate, 5, 1, 5),
        (zn_multiplication_candidate(4).candidate, 2, 1, None),
    ],
)
def test_inverse_of(
    candidate: FiniteGroupCandidate[int],
    element: int,
    identity_element: int,
    expected: int | None,
) -> None:
    assert run_or_skip(lambda: inverse_of(candidate, element, identity_element)) == expected


def test_inverse_of_returns_none_when_inverse_is_not_unique() -> None:
    candidate = multiple_inverse_candidate()

    assert run_or_skip(lambda: inverse_of(candidate, "x", "e")) is None


@pytest.mark.parametrize(
    ("candidate", "identity_element", "expected"),
    [
        (zn_addition_candidate(4).candidate, 0, True),
        (units_mod_candidate(12).candidate, 1, True),
        (zn_multiplication_candidate(4).candidate, 1, False),
        (multiple_inverse_candidate(), "e", False),
    ],
)
def test_has_inverses(
    candidate: FiniteGroupCandidate[object],
    identity_element: object,
    expected: bool,
) -> None:
    assert run_or_skip(lambda: has_inverses(candidate, identity_element)) is expected


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (zn_addition_candidate(4).candidate, True),
        (zn_multiplication_candidate(4).candidate, True),
        (units_mod_candidate(12).candidate, True),
        (nonassociative_candidate(), False),
    ],
)
def test_is_associative(candidate: FiniteGroupCandidate[int], expected: bool) -> None:
    assert run_or_skip(lambda: is_associative(candidate)) is expected


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (zn_addition_candidate(8).candidate, True),
        (units_mod_candidate(12).candidate, True),
        (z2_power_candidate(3).candidate, True),
        (dihedral_candidate(4).candidate, True),
        (zn_multiplication_candidate(4).candidate, False),
        (not_closed_candidate(), False),
        (no_identity_candidate(), False),
        (left_identity_only_candidate(), False),
        (nonassociative_candidate(), False),
    ],
)
def test_is_group(candidate: FiniteGroupCandidate[object], expected: bool) -> None:
    assert run_or_skip(lambda: is_group(candidate)) is expected


def test_is_group_returns_true_when_all_axiom_checks_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = zn_addition_candidate(2).candidate

    monkeypatch.setattr(ch03, "identity", lambda _candidate: 0)
    monkeypatch.setattr(ch03, "is_associative", lambda _candidate: True)
    monkeypatch.setattr(ch03, "has_inverses", lambda _candidate, _identity: True)
    monkeypatch.setattr(ch03, "is_closed", lambda _candidate: True)

    assert ch03.is_group(candidate) is True


def test_is_group_does_not_check_inverses_without_an_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_identity_is_missing(
        candidate: FiniteGroupCandidate[int],
        identity_element: int | None,
    ) -> bool:
        if identity_element is None:
            raise AssertionError("is_group checked inverses without an identity")
        return True

    monkeypatch.setattr(ch03, "has_inverses", fail_if_identity_is_missing)

    assert run_or_skip(lambda: ch03.is_group(no_identity_candidate())) is False


def test_is_group_returns_false_when_associativity_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = zn_addition_candidate(2).candidate

    monkeypatch.setattr(ch03, "identity", lambda _candidate: 0)
    monkeypatch.setattr(ch03, "is_associative", lambda _candidate: False)
    monkeypatch.setattr(ch03, "has_inverses", lambda _candidate, _identity: True)
    monkeypatch.setattr(ch03, "is_closed", lambda _candidate: True)

    assert ch03.is_group(candidate) is False


def test_is_group_returns_false_when_inverse_check_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = zn_addition_candidate(2).candidate

    monkeypatch.setattr(ch03, "identity", lambda _candidate: 0)
    monkeypatch.setattr(ch03, "is_associative", lambda _candidate: True)
    monkeypatch.setattr(ch03, "has_inverses", lambda _candidate, _identity: False)
    monkeypatch.setattr(ch03, "is_closed", lambda _candidate: True)

    assert ch03.is_group(candidate) is False


def test_is_group_returns_false_when_closure_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = zn_addition_candidate(2).candidate

    monkeypatch.setattr(ch03, "identity", lambda _candidate: 0)
    monkeypatch.setattr(ch03, "is_associative", lambda _candidate: True)
    monkeypatch.setattr(ch03, "has_inverses", lambda _candidate, _identity: True)
    monkeypatch.setattr(ch03, "is_closed", lambda _candidate: False)

    assert ch03.is_group(candidate) is False


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (zn_addition_candidate(8).candidate, True),
        (units_mod_candidate(12).candidate, True),
        (z2_power_candidate(3).candidate, True),
        (dihedral_candidate(4).candidate, False),
        (left_identity_only_candidate(), False),
    ],
)
def test_is_abelian(candidate: FiniteGroupCandidate[object], expected: bool) -> None:
    assert run_or_skip(lambda: is_abelian(candidate)) is expected


@pytest.mark.parametrize(
    ("subset", "expected"),
    [
        ({0}, True),
        ({0, 4}, True),
        ({0, 2, 4, 6}, True),
        ({0, 1, 2, 3, 4, 5, 6, 7}, True),
        ({0, 1}, False),
        ({0, 2, 5}, False),
        ({0, 8}, False),
        (set(), False),
    ],
)
def test_is_subgroup_for_z8_addition(subset: set[int], expected: bool) -> None:
    group = zn_addition_candidate(8).candidate

    assert run_or_skip(lambda: is_subgroup(group, subset)) is expected


@pytest.mark.parametrize(
    ("subset", "expected"),
    [
        ({(0, 0), (1, 0), (2, 0), (3, 0)}, True),
        ({(0, 0), (0, 1)}, True),
        ({(0, 0), (1, 0)}, False),
    ],
)
def test_is_subgroup_for_d4(subset: set[tuple[int, int]], expected: bool) -> None:
    group = dihedral_candidate(4).candidate

    assert run_or_skip(lambda: is_subgroup(group, subset)) is expected
