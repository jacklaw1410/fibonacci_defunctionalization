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


# > fibonacci(30, None)
# 832040
