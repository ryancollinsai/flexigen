// list_ops.flex
// List operations: sum, max, filter, double. Plus an adaptive sort that
// uses merge sort as baseline and switches to insertion sort for short lists.

let numbers = List<Int>[3, 7, 2, 9, 4, 6, 1, 8, 5, 10]

fn is_even(n: Int) -> Bool {
  return n % 2 == 0
}

fn double(n: Int) -> Int {
  return n * 2
}

fn sum(xs: List<Int>) -> Int {
  let total: Int = 0
  for x in xs {
    total = total + x
  }
  return total
}

fn max_val(xs: List<Int>) -> Int {
  let best: Int = xs[0]
  for x in xs {
    if x > best { best = x }
  }
  return best
}

print("Original list: " + numbers)
print("Sum: " + sum(numbers))
print("Max: " + max_val(numbers))

print("Even numbers doubled:")
for n in numbers {
  if is_even(n) {
    print(double(n))
  }
}

adaptive fn sort(xs: List<Int>) -> List<Int> {
  spec { ensure sorted(xs); optimize speed; keep stable }
  baseline { merge_sort(xs) }
  variant insertion when len(xs) < 32
}

let sorted_nums = sort(numbers)
print("Sorted: " + sorted_nums)
