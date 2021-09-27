# friendly-iter
Friendly iterator composition with support for easy fork/join multiprocessing.

This package provides classes that act as iterators and expose methods to manipulate these iterators, 
similar to Python built-ins such as `map` or `filter`.

## Compose Iterators in natural order

The following example crates an two iterators over squared prime numbers. The first uses `friendly-iter` and the
second vanilla Python.
The `friendly-iter` version specifies iterator transformations in the order they are applied: generate numbers, filter, and map.
In contrast, the plain Python version requires nested function calls in the reverse order of application.

```python
from friendly_iter import Iterator

def is_prime(x): raise NotImplementedError()

# Friendly-Iter
squared_primes = (Iterator(range(100))
                  .filter(is_prime)
                  .map(lambda x: x**2))

# Vanilla Python
squared_primes = map(lambda x: x**2, 
                     filter(is_prime, 
                            range(100)))
```

## Easy Parallelization

Say we compute an aggregation over data transformed by an expensive function.

```python
from friendly_iter import Iterator

def costly_transformation(x): raise NotImplementedError()

result = sum(Iterator(range(100))
             .map(costly_transformation))
```

It's easy to parallelize the expensive part of the iteration by inserting
a call to `.fork()` followed by `.join()`.

```python
from friendly_iter import Iterator

def costly_transformation(x): raise NotImplementedError()

result = sum(Iterator(range(100))
             .fork()
             .map(costly_transformation)
             .join())
```
