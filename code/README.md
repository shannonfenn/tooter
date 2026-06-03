# Code Exercises

This folder is script-first. The goal is to make AATA coding exercises easy to write, run, inspect, and then translate from Python to Rust.

## Python

Put runnable Python exercise files in `code/python/exercises/`.

Run one with `just`:

```sh
just py ch02
```

Or run it directly:

```sh
uv run python code/python/exercises/ch02.py
```

If a computation has a useful mathematical invariant, add an optional test in `code/python/tests/` and run:

```sh
uv run pytest
```

Tests are tests. They are not the point of the repo, and they are not a place to do exercises. Use small pytest/Hypothesis files when they sharpen feedback, such as verifying Bezout's identity for many inputs; otherwise ignore the folder and just run the exercise script.

## Rust

Put reusable Rust routines in the crate under `code/rust/aata_judson/src/`, and add a matching runnable example under `code/rust/aata_judson/examples/`.

The split exists because Cargo distinguishes library code from executable examples:

- `src/`: reusable functions and modules, such as `gcd` and `extended_gcd`.
- `examples/`: small runnable programs that call the library code and print useful output.

Run one with `just`:

```sh
just rs ch02
```

Or run it directly:

```sh
cargo run --example ch02
```

Run optional Rust tests:

```sh
cargo test
```

## Naming

Use chapter-prefixed names so the mapping is obvious:

- `ch02.py`
- `src/ch02.rs`
- `examples/ch02.rs`
- `test_ch02.py`

The learner-facing command should still be the same exercise name:

```sh
just exercise ch02
```
