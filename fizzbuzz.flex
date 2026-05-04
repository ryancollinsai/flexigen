// fizzbuzz.flex
// FizzBuzz from 1 to 30 in Flexigen syntax.

fn fizzbuzz(n: Int) -> String {
  if n % 15 == 0 { return "FizzBuzz" }
  if n % 3 == 0  { return "Fizz" }
  if n % 5 == 0  { return "Buzz" }
  return n
}

let i: Int = 1
while i <= 30 {
  print(fizzbuzz(i))
  i = i + 1
}
