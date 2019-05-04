import unittest
import unittest.mock

import loop.signal as signal


class TestSignal(unittest.TestCase):
    def test_empty(self):
        signals = signal.Signals()
        self.assertTrue(signals.empty())

    def test_add_signal(self):
        signals = signal.Signals()
        signals.add("SIGNAL1",lambda: None)
        signals.add("SIGNAL2", lambda: None)
        self.assertFalse(signals.empty())

    def test_count_signal_listeners(self):
        signals = signal.Signals()
        signals.add("SIGNAL1", lambda: None)
        signals.add("SIGNAL1", lambda: None)
        self.assertEqual(2, signals.count("SIGNAL1"))
        self.assertEqual(0, signals.count("SIGNAL_DOESN'T EXIST"))

    def test_remove_signal_listener(self):
        signals = signal.Signals()
        listener1 = lambda: None
        listener2 = lambda: None
        signals.add("SIGNAL", listener1)
        signals.remove("SIGNAL", listener2)
        self.assertEqual(1, signals.count("SIGNAL"))
        signals.remove("SIGNAL", listener1)
        self.assertEqual(0, signals.count("SIGNAL"))

    def test_call_signal_listeners(self):
        signals = signal.Signals()
        mock = unittest.mock.Mock()
        signals.add("SIGNAL1", lambda: mock(1))
        signals.add("SIGNAL2", lambda: mock(2))
        signals.add("SIGNAL1", lambda: mock(3))
        signals.call("SIGNAL1")
        self.assertEqual(2, mock.call_count)
        self.assertEqual([unittest.mock.call(1), unittest.mock.call(3)], mock.call_args_list)
