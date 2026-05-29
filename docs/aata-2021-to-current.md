# AATA 2021 to Current Notes

Checked on 2026-05-29.

The official AATA page lists the 2025 HTML edition as the latest annual edition, updated August 1, 2025. The Runestone edition is described as updated weekly. I did not find a separate official errata page for the 2021 print edition.

Use the upstream Git tags as the practical errata source:

- 2021 tag: `Annual-Edition-2021`
- current annual tag: `Annual-Edition-2025`

Generated reports live in `references/aata/diffs/`. Refresh them with:

```sh
scripts/update_aata_diff.sh
```

## High-Value Changes Since 2021

These are the changes most likely to matter while reading the 2021 physical copy.

- Chapter 3: Sage quaternion Cayley table correction for identifying `-1`.
- Chapter 5: Theorem 5.21 statement about the dihedral group generators was corrected.
- Chapter 8: Section 8.4 coset count corrected from the wrong exponent to `2^m`.
- Chapter 13: Lemma 13.8 proof typo corrected from a generic prime power to the indexed prime power.
- Chapter 14: Proposition 14.21 statement and proof wording corrected for induced permutation action on functions.
- Chapter 23: Lemma 23.29 root list corrected to include the missing factor in the final root term.
- Across chapters: many cross-reference, label, index, reading-question, URL, diagram, and Sage doctest updates.
- Sage updates: current PDF states testing against SageMath 10.6 and GAP 4.14.0.

## Practical Reading Rule

Read the physical 2021 copy first. Before doing exercises in a chapter, scan this file and optionally search the generated diff reports for that chapter source file:

```sh
rg "Chapter 5|Theorem 5.21|permute.xml" references/aata/diffs docs
```

For Sage material, prefer the 2025 PDF or Runestone because the online material has had the most maintenance.

