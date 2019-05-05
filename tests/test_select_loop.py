import time
import unittest
import unittest.mock

from loop.select_loop import SelectLoop
from loop.timer import Timers
from loop.signal import Signals
from loop.tick import FutureTickQueue


class TestSelectLoop(unittest.TestCase):
    def test_select_loop_timeout_emulation(self):
        mock = unittest.mock.Mock()
        event_loop = SelectLoop()
        event_loop.add_timer(0.05, mock)

        start = time.time()
        event_loop.launch()
        end = time.time()
        interval = end - start

        mock.assert_called_once()
        self.assertLessEqual(0.04, interval)

    def test_periodic_timer(self):
        mock = unittest.mock.Mock()
        event_loop = SelectLoop()
        timer = event_loop.add_periodic_timer(0.05, mock)
        event_loop.add_timer(0.12, lambda: event_loop.cancel_timer(timer))
        event_loop.launch()

        self.assertEqual(2, mock.call_count)

    def test_future_tick(self):
        mock = unittest.mock.Mock()
        event_loop = SelectLoop()
        event_loop.future_tick(lambda: mock(1))
        event_loop.future_tick(lambda: mock(2))
        event_loop.launch()

        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(2)],
            mock.call_args_list
        )

    def test_fututre_tick_earlier_than_timers(self):
        mock = unittest.mock.Mock()
        event_loop = SelectLoop()
        event_loop.add_timer(0, lambda: mock("timer 1"))
        event_loop.add_timer(0.03, lambda: mock("timer 2"))
        event_loop.add_timer(0, lambda: mock("timer 3"))
        event_loop.future_tick(lambda: mock("tick 1"))
        event_loop.future_tick(lambda: mock("tick 2"))
        event_loop.launch()

        self.assertEqual(
            [unittest.mock.call("tick 1"),
             unittest.mock.call("tick 2"),
             unittest.mock.call("timer 1"),
             unittest.mock.call("timer 3"),
             unittest.mock.call("timer 2")],
            mock.call_args_list
        )
