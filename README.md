# SpaceEagles Clipper · Window Selector

[![Local tests](https://img.shields.io/badge/local%20tests-4%20passing-2a7f62)](tests/test_selector.py) ![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB) ![Runtime dependencies](https://img.shields.io/badge/runtime%20dependencies-0-2a7f62)

A small, offline algorithm demo inspired by SpaceEagles Clipper. It receives scored time windows and chooses the highest-scoring set that does not overlap. It does not download, edit, or publish media.

```sh
python selector.py examples/synthetic.json --limit 2 --gap-ms 1000
python -m unittest discover -s tests -v
```

On the included synthetic fixture, the chosen `opening-beat` and `closing-beat` score **19** together. Taking the highest single candidate first scores **15** with the same clip limit because it blocks both.

The solver sorts candidates by end time and finds each compatible prefix with binary search. At each window it compares skipping against taking the window plus the best compatible prefix. A clip limit adds a second state dimension. Runtime is O(n log n) without a binding limit and O(n log n + nk) for a limit of k. Reconstruction follows the stored take/skip decisions.

Intervals are half open, timestamps are integer milliseconds, and ties are deterministic. Tests compare the solver against exhaustive search on small randomized fixtures, including a minimum gap, a clip count limit, and negative scores. Scores are inputs supplied by the caller; this demo does not claim to score editorial quality.

The examples are synthetic. This repository is a standalone demonstration with its own history.
