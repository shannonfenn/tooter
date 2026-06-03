# Code Exercises

This folder is script-first. The goal is to make AATA coding exercises easy to write, run, inspect, and then translate from Python to Rust.

## Python

Put runnable Python exercise files in `code/python/exercises/`.

Run one directly:

```sh
uv run python code/python/exercises/ch02_integers.py
```

If a computation has a useful mathematical invariant, add an optional check in `code/python/checks/` and run:

```sh
uv run pytest
```

Checks are not the point of the repo. Use them when they sharpen feedback, such as verifying Bezout's identity for many inputs.

## Rust

Put reusable Rust routines in the crate under `code/rust/aata_judson/src/`, and add a matching runnable example under `code/rust/aata_judson/examples/`.

Run one directly:

```sh
cargo run --example ch02_integers
```

Run optional Rust checks:

```sh
cargo test
```

## Naming

Use chapter-prefixed names so the mapping is obvious:

- `ch02_integers.py`
- `ch02_integers.rs`
- `test_ch02_integers.py`

