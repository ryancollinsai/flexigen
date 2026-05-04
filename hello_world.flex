// hello_world.flex — Flexigen Program 1
// Basic I/O, variables, and a simple function

let name: String = "World"
let version: Int = 1

fn greet(who: String) -> String {
  return "Hello, " + who + "! Welcome to Flexigen v" + version
}

fn square(n: Int) -> Int {
  return n * n
}

print(greet(name))
print("5 squared is: " + square(5))
print("10 squared is: " + square(10))

let scores = List<Int>[88, 92, 75, 61, 99]
let limit: Int = 90

fn clamp(x: Int) -> Int {
  if x > limit { return limit }
  else { return x }
}

print("Clamped scores:")
for n in scores {
  print(clamp(n))
}
