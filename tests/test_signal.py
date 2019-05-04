import unittest
import unittest.mock
import signal

from loop.signal import Signals


class TestSignal(unittest.TestCase):
    def test_empty(self):
        signals = Signals()
        self.assertTrue(signals.empty())

    def test_add_signal(self):
        signals = Signals()
        signals.add(signal.SIGUSR1, lambda: None)
        signals.add(signal.SIGUSR2, lambda: None)
        self.assertFalse(signals.empty())

    def test_count_signal_listeners(self):
        signals = Signals()
        signals.add(signal.SIGUSR1, lambda: None)
        signals.add(signal.SIGUSR1, lambda: None)
        self.assertEqual(2, signals.count(signal.SIGUSR1))
        self.assertEqual(0, signals.count(signal.SIGUSR2))

    def test_remove_signal_listener(self):
        signals = Signals()
        listener1 = lambda: None
        listener2 = lambda: None
        signals.add(signal.SIGUSR1, listener1)
        signals.remove(signal.SIGUSR1, listener2)
        self.assertEqual(1, signals.count(signal.SIGUSR1))
        signals.remove(signal.SIGUSR1, listener1)
        self.assertEqual(0, signals.count(signal.SIGUSR1))

    def test_call_signal_listeners(self):
        signals = Signals()
        mock = unittest.mock.Mock()
        signals.add(signal.SIGUSR1, lambda: mock(1))
        signals.add(signal.SIGUSR2, lambda: mock(2))
        signals.add(signal.SIGUSR1, lambda: mock(3))
        signals.call(signal.SIGUSR1)
        self.assertEqual(2, mock.call_count)
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(3)],
            mock.call_args_list
        )
