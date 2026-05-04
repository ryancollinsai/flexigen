// fibonacci.flex — Flexigen Program 2
// Demonstrates adaptive functions with multiple variants

adaptive fn fibonacci(n: Int) -> Int {
  spec { ensure exact; optimize speed }
  baseline { fib_recursive(n) }
  variant fib_iterative when n > 10
  variant fib_memoized when n > 30
}

fn fib_recursive(n: Int) -> Int {
  if n <= 1 { return n }
  return fib_recursive(n - 1) + fib_recursive(n - 2)
}

fn fib_iterative(n: Int) -> Int {
  if n <= 1 { return n }
  let a: Int = 0
  let b: Int = 1
  let i: Int = 2
  while i <= n {
    let c: Int = a + b
    a = b
    b = c
    i = i + 1
  }
  return b
}

print("Fibonacci sequence (first 12 terms):")
let i: Int = 0
while i <= 11 {
  print("fib(" + i + ") = " + fibonacci(i))
  i = i + 1
}
