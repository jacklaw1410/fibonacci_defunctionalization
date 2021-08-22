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

# fibonacci(10, None)
# > 55
