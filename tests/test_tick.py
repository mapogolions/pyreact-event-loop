import pytest
import unittest

import event_loop.tick


@pytest.fixture
def future_tick_queue():
    return event_loop.tick.FutureTickQueue()


def test_tick_queue_is_empty(future_tick_queue):
    assert future_tick_queue.empty()


def test_add_item_to_tick_queue(future_tick_queue):
    future_tick_queue.add(lambda: None)
    assert not future_tick_queue.empty()


def test_call_tick(future_tick_queue, mock):
    future_tick_queue.add(lambda: mock(1))
    future_tick_queue.add(lambda: mock(2))
    future_tick_queue.add(lambda: mock(3))
    future_tick_queue.tick()
    expected = [unittest.mock.call(1),
                unittest.mock.call(2),
                unittest.mock.call(3)]
    assert mock.call_args_list == expected
