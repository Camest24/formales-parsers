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
| `main.py` | Console program of Items 1 and 2: reads the grammar from standard input (`--sets`, `--tables` and `--trace` options) |
| `grammar.py` | Grammar reading, FIRST and FOLLOW sets, `--sets` output format (Item 1) |
| `slr.py` | LR(0) automaton, SLR(1) table and LR parser (Item 2) |
| `ll1.py` | LL(1) parsing table, LL(1) test and table-driven predictive parser (Item 2) |
| `sdd.py` | SDD evaluator: parse tree, dependency graph, topological order, evaluation (Item 3) |
| `test_grammar.py` | Unit tests for `grammar.py` |
| `test_ll1.py` | Unit tests for `ll1.py` |
| `test_slr.py` | Unit tests for `slr.py` |
| `test_sdd.py` | Unit tests for `sdd.py` |
| `app.py`, `web/index.html` | Web server and web page (bonus) |
| `informe.tex`, `informe.pdf` | Report (in Spanish) |
| `ejemplos/` | Inputs of the examples of the assignment, and our SDD files (`sdd_*.json`) |

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

After the grammar, the program decides whether it is LL(1) and/or SLR(1) and reads the strings to parse, one per line, until an empty line. The empty string is written as `e`. For each string it prints `yes` or `no`. The four cases of the assignment are handled as specified (menu `T` / `B` / `Q` when both parsers apply).

```
python main.py < ejemplos/ejemplo1.txt      # SLR(1) only
python main.py < ejemplos/ejemplo2.txt      # both: shows the T / B / Q menu
python main.py < ejemplos/ejemplo3.txt      # neither
python main.py < ejemplos/solo_ll1.txt      # LL(1) only
```

Expected output for `ejemplos/ejemplo1.txt`:

```
Grammar is SLR(1).
yes
yes
no
```

#### Tables and automaton (`--tables`)

With the `--tables` option, the program prints the LL(1) table, the LR(0) automaton (states and transitions) and the SLR(1) table:

```
python main.py --tables < ejemplos/gramatica_hechizo.txt
```

#### Step-by-step trace of the SLR(1) parser (`--trace`)

With the `--trace` option, the SLR(1) parser prints one line per step (the stack of states, the input that is left, and the action) before the `yes` / `no` answer of each string. Without the option, the output is exactly the one required by the assignment.

```
python main.py --trace < ejemplos/ejemplo1.txt
```

For example, typing the grammar `S -> (S) i` and the string `((i))` (menu option `B`) prints:

```
--- trace: ((i)) ---
Pila              Entrada     Acción
0                 ((i))$      shift 1
0 1               (i))$       shift 1
0 1 1             i))$        shift 3
0 1 1 3           ))$         reduce S -> i
0 1 1 4           ))$         shift 5
0 1 1 4 5         )$          reduce S -> ( S )
0 1 4             )$          shift 5
0 1 4 5           $           reduce S -> ( S )
0 2               $           accept
yes
```

The state numbers are only names given in the order in which the automaton states are discovered. The trace is also what the report uses to show a string parsed step by step.

### Item 3: SDD evaluator

The SDD is stored as data in a JSON file, so the evaluator knows nothing about a particular SDD. Our own SDD is `ejemplos/sdd_hechizo.json` ("magic spell score"): every element of a spell (`f` fire, `a` water, `t` earth, `v` wind) scores 1 point when it differs from the previous element, except the first one. It has an inherited attribute (`ant`, the previous element) and synthesized ones (`el`, `pts`).

```
python sdd.py ejemplos/sdd_hechizo.json < ejemplos/hechizos.txt
python sdd.py ejemplos/sdd_hechizo.json --graph < ejemplos/hechizos.txt     # also prints the dependency graph
```

The strings are read one per line until an empty line (`e` is the empty string). For a string that does not belong to the grammar it prints `no`. Otherwise it prints the annotated tree, the evaluation order and the value of the main attribute of `S`. For `faatv`:

```
Annotated tree:
S1 [pts=3]
  H1 [ant=n, pts=3]
    E1 [ant=n, el=f, pts=0]
      f1 [lexval=f]
    H2 [ant=f, pts=3]
...
S.pts = 3
```

If the dependency graph has a cycle, it prints `circular` and the cycle. `ejemplos/sdd_hechizo_circular.json` is the same SDD with one rule changed on purpose (`H1.ant = H.pts`), so `fa` is reported as circular.

Format of the JSON file:

- `grammar`: the grammar, with the same format as the standard input of Items 1 and 2.
- `attributes`: for each symbol, its attributes with `kind` (`synthesized` or `inherited`), `type` and `meaning`. The terminals only have `lexval`, which is the character itself.
- `main`: the attribute of `S` that is printed at the end.
- `rules`: for each production, a list of semantic rules written as `Symbol.attribute = expression`. A repeated nonterminal is told apart with a number (`H -> E H1`). The expressions can only use constants, `Symbol.attribute`, arithmetic, comparisons, `and` / `or` / `not`, `x if c else y` and `max`, `min`, `abs`, `len`, `str`, `int`. They are checked and evaluated by our own code (`eval` is never used).

Before evaluating, the program checks the SDD: `S` has no inherited attributes, and in every production each attribute is defined exactly once and only with attributes of that production.

### Web server (bonus)

```
python app.py
```

Then open `http://localhost:8000` in a browser (stop the server with `Ctrl+C`). The page has the grammar (our spell grammar by default), buttons for FIRST/FOLLOW and for the tables and automaton, a box to parse a string with LL(1) or SLR(1) (with the trace), and the SDD evaluator, where the SDD can be edited and the annotated tree is drawn.

The server only uses the standard library (`http.server`). It does not repeat any logic: each request calls the same functions as the console programs and returns JSON. The endpoints are:

| Endpoint | Request (JSON) | Response |
|---|---|---|
| `POST /api/sets` | `grammar` | FIRST and FOLLOW |
| `POST /api/tables` | `grammar` | LL(1) table, LR(0) automaton, SLR(1) table and which of the four cases the grammar is |
| `POST /api/parse` | `grammar`, `word`, `parser` (`T` or `B`) | `yes` / `no` and the SLR(1) trace |
| `POST /api/sdd` | `sdd` (the JSON text), `word` | annotated tree, dependency graph, order and value, or `circular` and the cycle |
| `GET /api/examples` | | the spell grammar and the SDD files of `ejemplos/` |

## Tests

```
python -m unittest test_grammar test_ll1 test_slr test_sdd -v
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

### SLR(1) parser (Sections 4.6.2, 4.6.3 and 4.6.4)

- **Augmented grammar**: the productions are numbered in a list and `S' -> S` is added as production 0.
- **LR(0) items** (4.6.2): a tuple `(production number, dot position)`. `closure` adds the productions of every nonterminal that follows a dot, until nothing changes. `goto(I, X)` moves the dot over `X` in the items that expect it and then applies `closure`. The canonical collection is built by exploring states from `closure({S' -> • S})`; each state is a `frozenset` of items.
- **SLR(1) table** (Algorithm 4.46): an arrow on a terminal gives a shift; an arrow on a nonterminal gives a GOTO entry; an item `A -> α •` gives a reduce on every terminal in FOLLOW(A); `S' -> S •` gives accept on `$`. If a cell would get two different actions, it is recorded as a conflict and the grammar is not SLR(1).
- **Parser** (Algorithm 4.44): a stack of states; shift pushes the target state, reduce pops one state per symbol of the production and pushes the GOTO of the state that is left.

### SDD evaluator (Sections 5.1 and 5.2)

- **Parse tree.** Our SLR(1) parser keeps a second stack with one node per symbol. A shift creates a terminal node (its `lexval` is the character). A reduce takes the last `len(production)` nodes as children of a new node for the head. The grammar of the SDD must be SLR(1).
- **Dependency graph** (5.2.1). One vertex per attribute of every node of the tree (for example `H2.ant`). For each semantic rule `X.a = f(Y.b, Z.c)` of the production used at a node, there is an edge from `Y.b` to `X.a` and from `Z.c` to `X.a`. The attributes used by a rule are found by reading the expression, so they are never listed twice.
- **Evaluation order** (5.2.2). A topological order of the graph (Kahn's algorithm: repeatedly take a vertex with no pending incoming edges). If some vertices are never taken, the SDD is circular for that string. The cycle is found by walking backwards through the vertices that were left.
- **Evaluation.** The attributes are computed in that order. The terminals already have their `lexval`.
- **Classification** (5.2.3 and 5.2.4). Our SDD is L-attributed and not S-attributed: `ant` is inherited, and every rule that defines it uses a constant, an attribute of the parent, or an attribute of a sibling to the left.

## Use of generative AI tools

We came up with the ideas and the structure, and the AI tools helped us turn them into code. For every algorithm we first read the book and worked it out by hand with small examples (FIRST and FOLLOW, LL(1) tables, LR(0) states, the SLR table, and the annotated tree and dependency graph of the SDD). Then we decided how to represent it (for example, ε as an empty list, or the SDD as a JSON file), asked the AI for the code, and reviewed and tested it against our hand results.

- **Claude** (Anthropic): explained the topics with analogies and interactive exercises, and helped us write the code of the modules, the tests, this README and the report. It also showed us Python functions and modules we did not know, such as `frozenset`, `setdefault`, `ast`, `contextlib.redirect_stdout` and `http.server`.
- **Gemini** (Google): translated and summarized sections of the book before we read them.
- **Claude Code**: made the commits and set up the GitHub repository.

The SDD (the spell idea, the attributes, the rules and the classification) was designed by Mariana through guided step-by-step exercises, and the hand-made examples were done by us.
