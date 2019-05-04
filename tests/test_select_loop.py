import unittest
import unittest.mock

from loop.select_loop import SelectLoop
from loop.timer import Timers
from loop.signal import Signals
from loop.tick import FutureTickQueue


class TestSelectLoop(unittest.TestCase):
    def test_check_initial_state(self):
        event_loop = SelectLoop()
        self.assertFalse(event_loop.running)
        self.assertIsInstance(event_loop.future_tick_queue, FutureTickQueue)
        self.assertIsInstance(event_loop.timers, Timers)
        self.assertIsInstance(event_loop.signals, Signals)
        self.assertEqual({}, event_loop.read_streams)
        self.assertEqual({}, event_loop.write_streams)
        self.assertEqual({}, event_loop.read_listeners)
        self.assertEqual({}, event_loop.write_listeners)
