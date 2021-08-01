# Defunctionalizing Fibonacci sequence

## What's this about?

I'm going to refactor a recursive Fibonacci function into an iterative one, using Python.

The topic is inspired by [James Koppel's post](http://www.pathsensitive.com/2019/07/the-best-refactoring-youve-never-heard.html).

## Fibonacci sequence

Let's first revisit what Fibonacci numbers are.

Each of them is the total of the two preceding members, starting with 0 and 1. Written in symbols:

```
F(0) = 0
F(1) = 1
F(n) = F(n - 1) + F(n - 2) for n > 1
```

You probably encountered something like this in your 101 programming class:

```py
def fibonacci(n: int):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)
```

This implementation is intuitive to most people and succinctly represent the mathematical definition.

## But...

So time for a "but". The naive recursive version is not practical for two reasons:

1. Each recursion calls itself two more times, so the time complexity is `O(2^n)`. It takes ages to compute even for small n like 50!
2. `n` is also bounded by the recursion limit. In Python you can check the limit with `sys.getrecursionlimit`.

  ```py
  import sys
  print(sys.getrecursionlimit())
  ```

OK I have to be honest to you that rewriting in iterative fashion _will not_ solve the time complexity issue.

I promise I will explain later why this is worth your time reading or even trying.

If you're only interested in the optimal solution, a little bit googling will bring you to an `O(n)` solution like [this](https://wiki.haskell.org/The_Fibonacci_sequence#With_state):

```py
def fibonacci_linear_time(n):
    f1 = 0
    f2 = 1
    for _ in range(n):
        f1, f2 = f1 + f2, f1
    return f1
```

## Let's start, shall we?
