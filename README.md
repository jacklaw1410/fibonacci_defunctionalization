# Defunctionalizing Fibonacci sequence

## What's this about?

I'm going to refactor a recursive Fibonacci function into an iterative one, using Python.

This is also a record of my learning from [James Koppel's post](http://www.pathsensitive.com/2019/07/the-best-refactoring-youve-never-heard.html).

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
def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)
```

This implementation is intuitive to most people and succinctly represents the mathematical nature.

## But...

So time for a "but". The naive recursive version is not practical for two reasons:

1. Each recursion calls itself two more times, so the time complexity is asymptotically `O(2^n)`. It takes ages to compute even for small n like 50!
2. `n` is also bounded by the recursion limit. In Python you can check the limit with `sys.getrecursionlimit`.

```py
import sys
print(sys.getrecursionlimit())
```

OK I have to be honest to you that rewriting in iterative fashion _will not_ solve the time complexity issue.

I promise I will explain later why this is worth your time reading and trying.

## "I want the answer"

If you're only interested in a faster solution, a little bit googling will bring you to an `O(n)` algorithm like [this](https://wiki.haskell.org/The_Fibonacci_sequence#With_state):

```py
def fibonacci_linear_time(n):
    f1 = 0
    f2 = 1
    for _ in range(n):
        f1, f2 = f1 + f2, f1
    return f1
```

If you dig deeper, you may also learn Fibonacci's closed form solution (which relates to the golden ratio), the exponentiation formula, memoization, fast doubling, stuff like that. There're plenty of faster algorithms in the wild!

## Let's defunctionalize, shall we?

Coming back to my task today - to defunctionalize the Fibonacci sequence, step by step.

You can find the corresponding code snippet of the following steps in `step_{n}.py`. (but some of them are rightfully broken code)

### Step 0: The starting point

Why don't we start with our cute yet totally useless recursive form?

For the sake of brevity, I will nudge the definition a bit - our sequence starts with `F(1) = F(2) = 1`:

```py
def fibonacci(n):
    if n <= 2:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)
```

So this setting gives us one recursive case and only one terminal case. The simpler the merrier.

### Step 1: First attempt at continuation passing

Notice that we could rewrite the else clause into this non-pythonic style:

```py
# ...
else:
    v = 0
    v += fibonacci(n - 1)
    v += fibonacci(n - 2)
    return v
```

Now we have two consecutive invocations of `fibonacci`. By the spirit of CPS conversion, let's make the second a callback to the first.

```py
# ...
else:
    v = 0
    # Looks weird to those familiar with JavaScript arrow function, right?
    def callback():
        v += fibonacci(n - 2)
    v += fibonacci(n - 1, callback)
    return v
```

And we need to tweak our `fibonacci` in order to take the callback as an argument. It now looks like:

```py
def fibonacci(n: int, kont: Callable[[], None]):
    if n <= 2:
        return kont()
    else:
        v = 0
        def callback():
            v += fibonacci(n - 2, kont)
        v += fibonacci(n - 1, callback)
        return v
```

This is not quite working, even despite the syntax problem. (Where is it?) `v` is reinitialized in every recursion. No accumulation is possible!

## Step 2: A deep dive into continuation

How could we rack up the value without resetting?

We need a "lazy version" of this callback so that you can defer the evaluation.

```python
# Works only if the sum is availabe right away
def callback():
    v += fibonacci(n - 2, kont)

# Taking the sum as input instead!
def callback(v: int):
    return v + fibonacci(n - 2, kont)
```

Secondly, we need a data structure to capture where we're. A function alone isn't quite enough, but we only care about what `n` is of interest at a particular moment:

```py
class Kont:
    n: int
    next: Optional[Kont]
```

(I'm using [the type hint syntax](https://docs.python.org/3/library/typing.html), which is available since Python 3.5. But in the code sample it will just be a `namedtuple`. Again, for the sake of brevity.)

It is a linked list by its own right, and also a manifestation of the _call stack_ of our recursion. We will drill down into this fact a bit later.

So finally we can refactor our `callback`. Observe that now this method need not live inside `fibonacci`.

- `n - 2` and `kont` can be unpacked from our `Kont` data structure.
- `v` is no longer bound by the closure of `fibonacci`.

Let's take it out and rename it to `apply` (a more conventional name):

```py
def apply(kont: Kont, v: int):
    return v + fibonacci(kont.n - 2, kont.next)
```

One last nuisance to deal with - what happens at the terminal condition?

By terminal condition it is asking what to start with for `fibonacci(5, ?)` if we'd like to evaluate `F(5)`.

Remember our `apply` is a lazy version of accumulating the sum. When you have nothing to add furtuer, the only sensible move is to return what you have attained so far, i.e. `v` itself.

```py
def apply(kont: Optional[Kont], v: int):
    if kont is not None:
        return v + fibonacci(kont.n - 2, kont.next)
    else:
        return v
```

Let's revisit where we leave off in Step 1:

```py
def fibonacci(n: int, kont: Callable[[], None]):
    if n <= 2:
        return kont()
    else:
        v = 0
        def callback():
            v += fibonacci(n - 2, kont)
        v += fibonacci(n - 1, callback)
        return v
```

In the terminal case `if n <= 2`, we replace `kont()` with

```py
if n <= 2:
    apply(kont, 1)
# ...
```

Besides actualizing `kont` by `apply` (`kont` is no longer a function that can be invoked), it also provides `1` as the "seed" for the entailing accumulation process.

(Question: If our terminal conditions are `F(0)` and `F(1)` instead, what differences are expected?)

For the recursive part, we pass the `Kont` data structure in place of the callback. We do `Kont(n, ...)` to preserve the current state of computation (and remember that `apply` does `kont.n - 2` for us).

```py
# ...
else:
    return fibonacci(n - 1, Kont(n, kont))
```

All in all, our `fibonacci` becomes:

```py
from collections import namedtuple
from typing import Optional

Kont = namedtuple('Kont', 'n next')

def apply(kont: Optional[Kont], v: int):
    if kont is not None:
        return v + fibonacci(kont.n - 2, kont.next)
    else:
        return v

def fibonacci(n: int, kont: Optional[Kont]):
    if n <= 2:
        return apply(kont, 1)
    else:
        return fibonacci(n - 1, Kont(n, kont))
```

And it's actually working! Try `fibonacci(10, None)`!

### Step 3: Putting everything back

Let me remind you our goal: an iterative version of the fibonacci function. The last step we need to go through is to somehow inline `apply`.

Before that we have to artifically create a while loop first because in our iterative version we can only `return` once. Remember the `v = 0` in Step 1? It's back again to allow accumulation!

```py
def fibonacci(n: int, kont: Optional[Kont]):
    v = 0
    while True:
        if n <= 2:
            return apply(kont, 1)
        else:
            return fibonacci(n - 1, Kont(n, kont))
```

Then we can inline `apply`:

```py
def fibonacci(n: int, kont: Optional[Kont]):
    v = 0
    while True:
        if n <= 2:
            if kont is not None:
                # substituting `v` by `1`
                return 1 + fibonacci(kont.n - 2, kont.next)
            else:
                return 1
        else:
            return fibonacci(n - 1, Kont(n, kont))
```

Do you see the tail-recursion form? In all `return`s the only non-trivial function is `fibonacci` itself.

Let's try to eliminate them one by one, starting from the `n > 2` case:

```py
# from
else:
    return fibonacci(n - 1, Kont(n, kont))
# to
else:
    kont = Kont(n, kont)
    n = n - 1
```

We must update `kont` first because we have preserve the current `n`. Order matters!

That leaves us the `n <= 2` case. We will first handle the inner else clause, i.e. when the termination is done.

```py
# from
if n <= 2:
    if kont is not None:
        # ...
    else:
        return 1
# to
if n <= 2:
    if kont is not None:
        # ...
    else:
        v += 1
        break
```

We exit the loop because `kont is None` means "no need to continue".

Only the final step remains. Let's eliminate for the case that `kont is not None`.

```py
# from
if n <= 2:
    if kont is not None:
        return 1 + fibonacci(kont.n - 2, kont.next)
    else:
        # ...
# to
if n <= 2:
    if kont is not None:
        v += 1
        n = kont.n - 2
        kont = Kont(n, kont.next)
    else:
        # ...
```

Note that we must compute `n = kont.n - 2` before reassigning `kont`. Order matters again.

We got our iterative Fibonacci function by putting pieces in place. Yay! 🎉🎉🎉

```py
from collections import namedtuple
from typing import Optional

Kont = namedtuple('Kont', 'n next')

def fibonacci(n: int, kont: Optional[Kont]):
    v = 0
    while True:
        if n <= 2:
            if kont is not None:
                v += 1
                n = kont.n - 2
                kont = kont.next
            else:
                v += 1
                break
        else:
            kont = Kont(n, kont)
            n = n - 1
    return v
```
