import pytest
import time
import unittest

import event_loop.timer


@pytest.fixture
def timers():
    return event_loop.timer.Timers()


def test_order_calls_of_timers(timers, mock):
    timers.add(event_loop.timer.Timer(0, lambda: mock(1)))
    timers.add(event_loop.timer.Timer(0, lambda: mock(2)))
    time.sleep(0.1)
    timers.tick()
    expected = [unittest.mock.call(1), unittest.mock.call(2)]
    assert mock.call_args_list == expected


def test_periodic_timer_will_be_left(timers, mock):
    timers.add(event_loop.timer.Timer(0, mock))
    timers.add(event_loop.timer.Timer(0, mock, periodic=True))
    time.sleep(0.1)
    timers.tick()
    assert mock.call_count == 2


def test_call_all_timers(timers, mock):
    for interval in [0, 0, 0]:
        timers.add(event_loop.timer.Timer(interval, mock))

    time.sleep(0.1)
    timers.tick()
    assert timers.empty()
    assert mock.call_count == 3


def test_call_one_timer(timers, mock):
    for interval in [3, 0, 4]:
        timers.add(event_loop.timer.Timer(interval, mock))

    time.sleep(0.1)
    timers.tick()
    mock.assert_called_once()


def test_eager_call_of_timers(timers, mock):
    for interval in [10, 5, 3]:
        timers.add(event_loop.timer.Timer(interval, mock))
    timers.tick()
    mock.assert_not_called()


def test_empty(timers):
    assert timers.empty()


def test_add_timer(timers):
    for interval in range(2, 5):
        timers.add(event_loop.timer.Timer(interval, lambda: None))

    assert not timers.empty()


def test_cancel_timer(timers):
    timer1 = event_loop.timer.Timer(0.1, lambda: None)
    timer2 = event_loop.timer.Timer(0.2, lambda: None)
    timers.add(timer1)
    assert timers.cancel(timer1)
    assert not timers.cancel(timer2)


def test_get_first_timer(timers):
    for interval in range(4, 8):
        timers.add(event_loop.timer.Timer(interval, lambda: None))

    _, first_timer = timers.get_first()
    assert first_timer.interval == 4


def test_get_first_timer_if_schedule_is_empty(timers):
    timers = event_loop.timer.Timers()
    assert timers.get_first() is None


def test_get_time(timers):
    assert timers.time is None
    assert time.time() <= timers.get_time()
    assert time.time() >= timers.get_time()


def test_contains(timers, mock):
    timer1 = event_loop.timer.Timer(0.1, mock)
    timer2 = event_loop.timer.Timer(0.1, mock)
    timer3 = event_loop.timer.Timer(0.4, mock)
    timers.add(timer1)
    timers.add(timer2)
    assert timer1 in timers
    assert timer2 in timers
    assert timer3 not in timers
