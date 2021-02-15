import time

from friendly_iter import Iterator


def listify(x):
    return [x + 10, x + 20, x + 30]


def is_negative(x):
    return x < 0


def delay(x):
    time.sleep(0.01)
    return x


def test_serial_filter_out_all_items():
    it = Iterator(range(10))
    it.filter(is_negative)

    result = list(it)

    assert result == []


def test_serial_produce_more_items():
    it = Iterator(range(3))
    it.map(listify)
    it.flatten()

    result = list(it)

    assert result == [10, 20, 30, 11, 21, 31, 12, 22, 32]


def test_parallel_filter_out_all_items():
    it = Iterator(range(10))
    it = it.fork()
    it.map(delay)
    it.filter(is_negative)
    it = it.join()

    result = list(it)

    assert result == []


def test_parallel_produce_more_items():
    it = Iterator(range(3))
    it = it.fork()
    it.map(delay)
    it.map(listify)
    it.flatten()
    it = it.join()

    result = set(it)

    assert result == {10, 20, 30, 11, 21, 31, 12, 22, 32}


def test_parallel_iteration_works_with_items_that_cant_be_compared():
    """e.g. numpy arrays, or pandas series used to cause problems"""

    it = Iterator([DontCompareMe()])
    it = it.fork()
    it = it.join()

    result = list(it)

    assert len(result) == 1


class DontCompareMe:
    def __eq__(self, other):
        raise TypeError("Oh naughty, you did it!")
