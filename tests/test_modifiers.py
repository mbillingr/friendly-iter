from unittest.mock import Mock

import pytest

from friendly_iter.iterator_modifiers import flatten, take, skip, step


def test_flatten():
    result = flatten([range(4), [], [4, 5]])
    assert list(result) == [0, 1, 2, 3, 4, 5]


def test_take_limits_number_of_resulting_items():
    result = take(3, range(10))
    assert list(result) == [0, 1, 2]


def test_take_works_if_iterator_is_too_short():
    result = take(10, range(3))
    assert list(result) == [0, 1, 2]


def test_skip_drops_first_n_elements():
    result = skip(2, [1, 2, 3, 4, 5])
    assert list(result) == [3, 4, 5]


def test_skipping_too_many_results_in_empty_iterator():
    result = skip(3, [1, 2])
    assert list(result) == []


def test_skip_advanced_iterator_lazily():
    skip(3, FailingIter())  # should not raise


def test_refuse_stepsize_less_than_one():
    with pytest.raises(ValueError):
        step(0, [])


def test_step_size_one_is_an_identity_operation():
    it = Mock()
    result = step(1, it)
    assert result is it


def test_step_always_yields_first_element():
    result = step(2, [1])
    assert list(result) == [1]


def test_step_yields_every_nth_item():
    result = step(2, [1, 2, 3, 4])
    assert list(result) == [1, 3]


class FailingIter:
    def __iter__(self):
        return self

    def __next__(self):
        pytest.fail("Iterator was advanced")
