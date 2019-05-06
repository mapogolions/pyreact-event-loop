import unittest
import unittest.mock
import signal

from loop.signal import Signals


class TestSignal(unittest.TestCase):
    def setUp(self):
        self.signals = Signals()

    def test_empty(self):
        self.assertTrue(self.signals.empty())

    def test_add_signal(self):
        self.signals.add(signal.SIGUSR1, lambda: None)
        self.signals.add(signal.SIGUSR2, lambda: None)
        self.assertFalse(self.signals.empty())

    def test_count_signal_listeners(self):
        self.signals.add(signal.SIGUSR1, lambda: None)
        self.signals.add(signal.SIGUSR1, lambda: None)
        self.assertEqual(2, self.signals.count(signal.SIGUSR1))
        self.assertEqual(0, self.signals.count(signal.SIGUSR2))

    def test_remove_signal_listener(self):
        listener1 = lambda: None
        listener2 = lambda: None
        self.signals.add(signal.SIGUSR1, listener1)
        self.signals.remove(signal.SIGUSR1, listener2)
        self.assertEqual(1, self.signals.count(signal.SIGUSR1))
        self.signals.remove(signal.SIGUSR1, listener1)
        self.assertEqual(0, self.signals.count(signal.SIGUSR1))

    def test_call_signal_listeners(self):
        mock = unittest.mock.Mock()
        self.signals.add(signal.SIGUSR1, lambda: mock(1))
        self.signals.add(signal.SIGUSR2, lambda: mock(2))
        self.signals.add(signal.SIGUSR1, lambda: mock(3))
        self.signals.call(signal.SIGUSR1)
        self.assertEqual(2, mock.call_count)
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(3)],
            mock.call_args_list
        )
