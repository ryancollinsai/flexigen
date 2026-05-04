// data_analysis.flex — Flexigen Complex Program
// Adaptive duplicate detection, statistics, and reporting

adaptive fn has_duplicates(a: List<Int>) -> Bool {
  spec { ensure exact; optimize speed }
  baseline { nested_scan(a) }
  variant hashset_scan
  variant bitmap_scan when max_val(a) < 1000000
}

fn nested_scan(a: List<Int>) -> Bool {
  let i: Int = 0
  while i < len(a) {
    let j: Int = i + 1
    while j < len(a) {
      if a[i] == a[j] { return true }
      j = j + 1
    }
    i = i + 1
  }
  return false
}

fn mean(xs: List<Int>) -> Int {
  let total: Int = 0
  for x in xs { total = total + x }
  return total / len(xs)
}

fn max_val(xs: List<Int>) -> Int {
  let best: Int = xs[0]
  for x in xs {
    if x > best { best = x }
  }
  return best
}

fn min_val(xs: List<Int>) -> Int {
  let smallest: Int = xs[0]
  for x in xs {
    if x < smallest { smallest = x }
  }
  return smallest
}

fn len(xs: List<Int>) -> Int {
  let count: Int = 0
  for x in xs { count = count + 1 }
  return count
}

fn count_above(xs: List<Int>, threshold: Int) -> Int {
  let count: Int = 0
  for x in xs {
    if x > threshold { count = count + 1 }
  }
  return count
}

// Dataset A — no duplicates
let dataset_a = List<Int>[10, 25, 37, 42, 58, 61, 79, 83, 91, 100]

// Dataset B — has duplicates
let dataset_b = List<Int>[5, 12, 33, 12, 47, 5, 88, 91, 33, 100]

print("=== Flexigen Data Analysis Report ===")
print("")
print("--- Dataset A ---")
print("Values: " + dataset_a)
print("Length: " + len(dataset_a))
print("Mean:   " + mean(dataset_a))
print("Min:    " + min_val(dataset_a))
print("Max:    " + max_val(dataset_a))
print("Has duplicates: " + has_duplicates(dataset_a))
print("Count above 50: " + count_above(dataset_a, 50))

print("")
print("--- Dataset B ---")
print("Values: " + dataset_b)
print("Length: " + len(dataset_b))
print("Mean:   " + mean(dataset_b))
print("Min:    " + min_val(dataset_b))
print("Max:    " + max_val(dataset_b))
print("Has duplicates: " + has_duplicates(dataset_b))
print("Count above 50: " + count_above(dataset_b, 50))

print("")
print("=== End of Report ===")
