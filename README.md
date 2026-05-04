# Flexigen 🔁

**A Self-Adapting Programming Language**  
CS 420-04 · Spring 2026  
*Nikhil Maharaj · Ryan Collins · Chris Sapien*

---

## What Is Flexigen?

Flexigen is a language for writing programs that adapt their own implementations while preserving the programmer's intent. You declare **what** must stay true; the runtime picks **how** — and picks again when your data changes.

## Quick Start

```bash
# Run a single program
python3 interpreter/flexigen.py programs/hello_world.flex

# Run all programs
python3 interpreter/flexigen.py programs/fibonacci.flex
python3 interpreter/flexigen.py programs/list_ops.flex
python3 interpreter/flexigen.py programs/fizzbuzz.flex
python3 interpreter/flexigen.py programs/data_analysis.flex
```

## Programs

| File | Type | Demonstrates |
|------|------|--------------|
| `hello_world.flex` | Simple | Variables, functions, string concat, for loops |
| `fibonacci.flex` | Simple | Adaptive fn, variant conditions (n > 10 → iterative) |
| `list_ops.flex` | Simple | List ops, filtering, adaptive sort |
| `fizzbuzz.flex` | FizzBuzz | Modulo, conditionals, while loop |
| `data_analysis.flex` | Complex | Adaptive dup detection, stats, full report |

## Syntax Overview

```flex
// Variables
let name: String = "World"
let mut count: Int = 0

// Functions
fn square(n: Int) -> Int {
  return n * n
}

// Adaptive Functions
adaptive fn sort(xs: List<Int>) -> List<Int> {
  spec {
    ensure sorted(xs)   // invariant — never broken
    optimize speed      // goal
    keep stable         // extra constraint
  }
  baseline { merge_sort(xs) }              // always correct
  variant timsort    when mostly_sorted(xs) // runtime switch
  variant insertion  when len(xs) < 32     // runtime switch
}

// Control Flow
for n in scores { print(n) }
while i < 10 { i = i + 1 }
if x > limit { return limit } else { return x }
```

## Types

`Int`, `Float`, `Bool`, `String`, `Bytes`, `List<T>`, `Map<K,V>`, `Set<T>`, `Option<T>`, `Result<T,E>`

## The Adaptive Model

Every adaptive function has four parts:
1. **`spec`** — fixed contract (ensure, optimize, keep)
2. **`baseline`** — always-correct trusted reference
3. **`variant`** — conditional alternatives with `when` guards
4. **`report`** — every adaptation decision is logged

## Interpreter Architecture

```
Source (.flex)
    ↓ Lexer (tokenizes)
Tokens
    ↓ Parser (builds AST)
AST (Abstract Syntax Tree)
    ↓ Interpreter (tree-walk evaluator)
Output + Adaptation Report
```

## Website

Open `index.html` in any browser for the full language website with live code examples and program outputs.

## Challenges & Limitations

- Proving semantic equivalence for arbitrary rewrites is hard — early Flexigen relies on contracts + tests + limited transformations
- Profiling adds overhead — adaptive behavior may be unsuitable for safety-critical systems without strict mode
- Debugging requires excellent logs, version pinning, and reproducible adaptation decisions
