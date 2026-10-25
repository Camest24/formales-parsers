# First/Follow, LL(1) and SLR(1) Parsers, and SDD Evaluator

Formal Languages (SI2002) — EAFIT University — Final Project

## Authors

- Juan Camilo Estrada Rave
- Mariana Salomé Velásquez Gallego

Class number: SI2002-4368 (Formal Languages, 2026-2)

## Environment

- Operating system: Windows 11
- Language: Python 3.12.7 (standard library only)
- Testing: `unittest` (included with Python)

## Project structure

| File | Contents |
|---|---|
| `main.py` | Console program: reads the grammar from standard input (`--sets` option) |
| `grammar.py` | Grammar reading, FIRST and FOLLOW sets, `--sets` output format (Item 1) |
| `test_grammar.py` | Unit tests for `grammar.py` |
| `ejemplos/` | Inputs of the three examples of the assignment |

<!-- TODO: add ll1.py, slr.py, sdd.py and app.py as we create them -->

## How to run

### Item 1: FIRST and FOLLOW

The program reads the grammar from standard input. With the `--sets` option, it prints the FIRST and FOLLOW sets:

```
python main.py --sets < ejemplos/ejemplo2.txt
```

Expected output:

```
First(A) = {a, d}
First(B) = {b, e}
First(S) = {a, d}
Follow(A) = {b, $}
Follow(B) = {c, $}
Follow(S) = {$}
```

The grammar can also be typed by hand: run `python main.py --sets` and write it line by line.

### Item 2: LL(1) and SLR(1) parsers

<!-- TODO -->

### Item 3: SDD evaluator

<!-- TODO -->

### Web server (bonus)

<!-- TODO -->

## Tests

```
python -m unittest test_grammar -v
```

## Algorithms

All algorithms follow Aho et al., *Compilers: Principles, Techniques, and Tools* (2nd edition).

### FIRST and FOLLOW (Section 4.4.2)

- **Grammar representation.** A dictionary that maps each nonterminal to its list of alternatives. Each alternative is a list of symbols, and ε is the empty list. For example, `B -> bBc e` is stored as `{"B": [["b", "B", "c"], []]}`. Inside the FIRST and FOLLOW sets, ε is written `e`, as in the output format.
- **FIRST of a string** `X1 X2 ... Xn`: add FIRST(X1) without ε; if X1 can derive ε, continue with X2, and so on. If every symbol can derive ε (or the string is empty), add ε.
- **FIRST of every nonterminal**: start with empty sets and apply the rule above to every alternative, repeating until no set changes. Left-recursive alternatives (such as `S -> S+T`) do not add anything new, so the loop always ends.
- **FOLLOW**: put `$` in FOLLOW(S). For every occurrence of a nonterminal X in an alternative of A, add FIRST of what is to the right of X (without ε). If X is at the end, or everything to its right can derive ε, add FOLLOW(A) to FOLLOW(X). Repeat until no set changes.

## Use of generative AI tools

<!-- TODO: write the final summary from notas/uso_ia.md before submitting -->
