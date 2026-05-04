# Flexigen

A self-adapting programming language.
CS 420-04, Spring 2026
Nikhil Maharaj, Ryan Collins, Chris Sapien

## What is Flexigen?

Flexigen is a language for programs that change their own implementation at runtime without losing correctness. You write the rules that have to hold. The runtime picks an implementation that satisfies them, and picks a different one when the input changes.

## Quick start

```bash
# Run a single program
python flexigen.py hello_world.flex

# Other programs in the repo
python flexigen.py fibonacci.flex
python flexigen.py list_ops.flex
python flexigen.py fizzbuzz.flex
python flexigen.py data_analysis.flex
```

## Programs

| File | Type | What it shows |
|------|------|---------------|
| hello_world.flex | Simple | Variables, functions, string concat, for loops |
| fibonacci.flex | Simple | Adaptive function. When n > 10 the iterative variant is picked instead of the recursive baseline |
| list_ops.flex | Simple | List operations, filtering, an adaptive sort |
| fizzbuzz.flex | FizzBuzz | Modulo, conditionals, while loop |
| data_analysis.flex | Complex | Adaptive duplicate detection, summary stats, a printed report |

## Syntax

```flex
// Variables
let name: String = "World"
let mut count: Int = 0

// Functions
fn square(n: Int) -> Int {
  return n * n
}

// Adaptive functions
adaptive fn sort(xs: List<Int>) -> List<Int> {
  spec {
    ensure sorted(xs)   // invariant the runtime cannot break
    optimize speed      // what to optimize for
    keep stable         // extra constraint
  }
  baseline { merge_sort(xs) }
  variant timsort    when mostly_sorted(xs)
  variant insertion  when len(xs) < 32
}

// Control flow
for n in scores { print(n) }
while i < 10 { i = i + 1 }
if x > limit { return limit } else { return x }
```

## Types

`Int`, `Float`, `Bool`, `String`, `Bytes`, `List<T>`, `Map<K,V>`, `Set<T>`, `Option<T>`, `Result<T,E>`

## How an adaptive function is built

Every adaptive function has four parts.

`spec` is the contract. It says what the function must guarantee (`ensure`), what to optimize (`optimize`), and any extra constraints (`keep`). A variant that violates the contract gets rejected.

`baseline` is the implementation that is always allowed to run. It is the trusted reference. Variants are compared against it.

`variant` is a candidate implementation guarded by a `when` clause. The runtime evaluates the clause, picks the first matching variant, and falls back to baseline if nothing matches.

`report` is the running log of which variant ran and why. It prints at the end of a program run, and can be replayed to reconstruct an exact execution.

## How the interpreter works

```
Source (.flex)
    -> Lexer    (tokens)
    -> Parser   (AST)
    -> Interpreter (tree-walker)
    -> Output + Adaptation Report
```

## Website

The full landing page is in `index.html`. Open it locally in a browser, or visit https://ryancollinsai.github.io/flexigen/.

## What is not in this prototype

Equivalence checking is hard. Flexigen does not currently prove that a variant is semantically equal to the baseline. It runs the same tests against both and trusts the result. A real version would need formal proofs for the cases that matter.

The runtime does not measure variant cost yet. Compile-time guards are real, but the choice of which variant wins is not driven by live profile data.

The `propose ai variant` block is recognized by the lexer and parser. The implementation is not wired in.

## Honor pledge

I have neither given nor received unauthorized aid in completing this work, nor have I presented someone else's work as my own.
