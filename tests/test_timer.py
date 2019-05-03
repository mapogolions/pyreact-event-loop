import unittest
import unittest.mock
import time

import loop.timer as timer


class TestTimer(unittest.TestCase):
    def test_empty(self):
        timers = timer.Timers()
        self.assertTrue(timers.empty())

    def test_add_timer(self):
        timers = timer.Timers()
        for interval in range(1, 4):
            timers.add(timer.Timer(interval, lambda: None))
        self.assertFalse(timers.empty())
        self.assertEqual(3, len(timers.schedule))
        self.assertEqual(3, len(timers.timers))

    def test_cancel_timer(self):
        timers = timer.Timers()
        timer1 = timer.Timer(0.1, lambda: None)
        timer2 = timer.Timer(0.2, lambda: None)
        timers.add(timer1)
        self.assertTrue(timers.cancel(timer1))
        self.assertFalse(timers.cancel(timer2))

    def test_get_first_timer(self):
        timers = timer.Timers()
        for interval in range(4, 8):
            timers.add(timer.Timer(interval, lambda: None))
        (_, first) = timers.get_first()
        self.assertEqual(4, first.interval)

    def test_get_time(self):
        timers = timer.Timers()
        self.assertIsNone(timers.time)
        self.assertLessEqual(time.time(), timers.get_time())
        self.assertGreaterEqual(time.time(), timers.get_time())

    def test_contains(self):
        timers = timer.Timers()
        timer1 = timer.Timer(0.1, lambda: True)
        timer2 = timer.Timer(0.1, lambda: False)
        timer3 = timer.Timer(0.4, lambda: None)
        timers.add(timer1)
        timers.add(timer2)
        self.assertIn(timer1, timers)
        self.assertIn(timer2, timers)
        self.assertNotIn(timer3, timers)
