def fibonacci(n: int, kont: Callable[[], None]):
    if n <= 2:
        return kont()
    else:
        v = 0
        def callback():
            v += fibonacci(n - 2, kont)
        v += fibonacci(n - 1, callback)
        return v

# This is NOT valid code.
