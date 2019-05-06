import unittest
import unittest.mock
import time

from loop.timer import Timer, Timers


class TestTimer(unittest.TestCase):
    def setUp(self):
        self.timers = Timers()
        self.mock = unittest.mock.Mock()

    def test_order_calls_of_timers(self):
        self.timers.add(Timer(0, lambda: self.mock(1)))
        self.timers.add(Timer(0, lambda: self.mock(2)))

        time.sleep(0.1)
        self.timers.tick()

        self.assertTrue(self.timers.empty())
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(2)],
            self.mock.call_args_list
        )

    def test_periodic_timer_will_be_left(self):
        self.timers.add(Timer(0, self.mock))
        self.timers.add(Timer(0, self.mock, periodic=True))

        time.sleep(0.1)
        self.timers.tick()

        self.assertEqual(2, self.mock.call_count)

    def test_call_all_timers(self):
        for interval in [0, 0, 0]:
            self.timers.add(Timer(interval, self.mock))

        time.sleep(0.1)
        self.timers.tick()

        self.assertTrue(self.timers.empty())
        self.assertEqual(3, self.mock.call_count)

    def test_call_one_timer(self):
        for interval in [3, 0, 4]:
            self.timers.add(Timer(interval, self.mock))

        time.sleep(0.1)
        self.timers.tick()

        self.assertFalse(self.timers.empty())
        self.assertEqual(1, self.mock.call_count)
        self.assertEqual(2, len(self.timers.timers))
        self.assertEqual(2, len(self.timers.schedule))

    def test_eager_call_of_timers(self):
        for interval in [10, 5, 3]:
            self.timers.add(Timer(interval, self.mock))

        self.timers.tick()

        self.assertFalse(self.timers.empty())
        self.assertEqual(0, self.mock.call_count)

    def test_empty(self):
        self.assertTrue(self.timers.empty())

    def test_add_timer(self):
        for interval in range(2, 5):
            self.timers.add(Timer(interval, lambda: None))
        self.assertFalse(self.timers.empty())
        self.assertEqual(3, len(self.timers.schedule))
        self.assertEqual(3, len(self.timers.timers))

    def test_cancel_timer(self):
        timer1 = Timer(0.1, lambda: None)
        timer2 = Timer(0.2, lambda: None)
        self.timers.add(timer1)
        self.assertTrue(self.timers.cancel(timer1))
        self.assertFalse(self.timers.cancel(timer2))

    def test_get_first_timer(self):
        for interval in range(4, 8):
            self.timers.add(Timer(interval, lambda: None))
        _, first = self.timers.get_first()
        self.assertEqual(4, first.interval)

    def test_get_first_timer_if_schedule_is_empty(self):
        timers = Timers()
        self.assertIsNone(timers.get_first())

    def test_get_time(self):
        self.assertIsNone(self.timers.time)
        self.assertLessEqual(time.time(), self.timers.get_time())
        self.assertGreaterEqual(time.time(), self.timers.get_time())

    def test_contains(self):
        timer1 = Timer(0.1, lambda: True)
        timer2 = Timer(0.1, lambda: False)
        timer3 = Timer(0.4, lambda: None)
        self.timers.add(timer1)
        self.timers.add(timer2)
        self.assertIn(timer1, self.timers)
        self.assertIn(timer2, self.timers)
        self.assertNotIn(timer3, self.timers)
