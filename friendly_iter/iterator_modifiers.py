from typing import Iterator, Iterable


def flatten(iterator: Iterable) -> Iterator:
    for inner in iterator:
        yield from inner


def take(n: int, iterator: Iterable) -> Iterator:
    for _, x in zip(range(n), iterator):
        yield x


def skip(n: int, iterator: Iterable) -> Iterator:
    i = iter(iterator)
    for _, _ in zip(range(n), i):
        pass  # ignore first n elements
    yield from i


def step(n: int, iterator: Iterable) -> Iterator:
    if n < 1:
        raise ValueError("step size must be an integer greater than zero")
    elif n == 1:
        return iterator
    else:
        return _step(n, iter(iterator))


def _step(n, iterator):
    try:
        while True:
            yield next(iterator)
            for _ in range(n - 1):
                next(iterator)
    except StopIteration:
        pass
