import pytest
import signal
import unittest

import event_loop.signal


@pytest.fixture
def signals():
    return event_loop.signal.Signals()


def test_no_registered_signals(signals):
    assert signals.empty()


def test_add_signal(signals):
    signals.add(signal.SIGUSR1, lambda: None)
    signals.add(signal.SIGUSR2, lambda: None)
    assert not signals.empty()


def test_count_signal_listeners(signals):
    signals.add(signal.SIGUSR1, lambda: None)
    signals.add(signal.SIGUSR1, lambda: None)
    assert signals.count(signal.SIGUSR1) == 2
    assert signals.count(signal.SIGUSR2) == 0


def test_remove_signal_listener(signals, mock):
    signals.add(signal.SIGUSR1, mock)
    assert signals.count(signal.SIGUSR1) == 1
    signals.remove(signal.SIGUSR1, mock)
    assert signals.count(signal.SIGUSR1) == 0


def test_call_signal_listeners(signals, mock):
    signals.add(signal.SIGUSR1, lambda: mock(1))
    signals.add(signal.SIGUSR2, lambda: mock(2))
    signals.add(signal.SIGUSR1, lambda: mock(3))
    signals.call(signal.SIGUSR1)
    expected = [unittest.mock.call(1), unittest.mock.call(3)]
    assert mock.call_args_list == expected
