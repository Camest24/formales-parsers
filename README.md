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
| `ll1.py` | LL(1) parsing table, LL(1) test and table-driven predictive parser (Item 2) |
| `test_grammar.py` | Unit tests for `grammar.py` |
| `test_ll1.py` | Unit tests for `ll1.py` |
| `ejemplos/` | Inputs of the three examples of the assignment |

<!-- TODO: add slr.py, sdd.py and app.py as we create them -->

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

After the grammar, the program decides whether it is LL(1) and/or SLR(1) and reads the strings to parse, one per line, until an empty line. The empty string is written as `e`. For each string it prints `yes` or `no`.

```
python main.py < ejemplos/ejemplo2_ll1.txt
```

Expected output (the grammar of Example 2 is LL(1); the strings are `d`, `adbc`, `a` and the empty string):

```
Grammar is LL(1).
yes
yes
no
no
```

<!-- TODO: SLR(1) and the T / B / Q menu (case 1). Until slr.py exists, every grammar that is not LL(1) is reported as neither. -->

### Item 3: SDD evaluator

<!-- TODO -->

### Web server (bonus)

<!-- TODO -->

## Tests

```
python -m unittest test_grammar test_ll1 -v
```

## Algorithms

All algorithms follow Aho et al., *Compilers: Principles, Techniques, and Tools* (2nd edition).

### FIRST and FOLLOW (Section 4.4.2)

- **Grammar representation.** A dictionary that maps each nonterminal to its list of alternatives. Each alternative is a list of symbols, and ε is the empty list. For example, `B -> bBc e` is stored as `{"B": [["b", "B", "c"], []]}`. Inside the FIRST and FOLLOW sets, ε is written `e`, as in the output format.
- **FIRST of a string** `X1 X2 ... Xn`: add FIRST(X1) without ε; if X1 can derive ε, continue with X2, and so on. If every symbol can derive ε (or the string is empty), add ε.
- **FIRST of every nonterminal**: start with empty sets and apply the rule above to every alternative, repeating until no set changes. Left-recursive alternatives (such as `S -> S+T`) do not add anything new, so the loop always ends.
- **FOLLOW**: put `$` in FOLLOW(S). For every occurrence of a nonterminal X in an alternative of A, add FIRST of what is to the right of X (without ε). If X is at the end, or everything to its right can derive ε, add FOLLOW(A) to FOLLOW(X). Repeat until no set changes.

### LL(1) table and parser (Sections 4.4.3 and 4.4.4)

- **Parsing table** (Algorithm 4.31): for each production `A -> α`, add it to `M[A, a]` for every terminal `a` in FIRST(α); if ε is in FIRST(α), also add it to `M[A, b]` for every `b` in FOLLOW(A) (including `$`). Each cell stores a list of productions.
- **LL(1) test**: the grammar is LL(1) if and only if no cell has more than one production. The grammar is never transformed before this test.
- **Parser** (Algorithm 4.34): a stack (a Python list whose last element is the top) starts as `[$, S]`, and `$` is appended to the input. If the top equals the current input symbol, both are consumed; if the top is a nonterminal, it is replaced by the production in `M[top, symbol]`, pushed in reverse order. The string is accepted when both the stack and the input reach `$`; any other case is an error.

## Use of generative AI tools

<!-- TODO: write the final summary from notas/uso_ia.md before submitting -->
