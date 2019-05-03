import unittest
import unittest.mock
import time

import loop.timer as timer


class TestTimer(unittest.TestCase):
    def test_order_calls_of_timers(self):
        mock = unittest.mock.Mock()
        timers = timer.Timers()
        timers.add(timer.Timer(0, lambda: mock(1)))
        timers.add(timer.Timer(0, lambda: mock(2)))

        time.sleep(0.1)
        timers.tick()

        self.assertTrue(timers.empty())
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(2)],
            mock.call_args_list
        )

    def test_periodic_timer_will_be_left(self):
        mock = unittest.mock.Mock()
        timers = timer.Timers()
        timers.add(timer.Timer(0, lambda: mock()))
        timers.add(timer.Timer(0, lambda: mock(), periodic=True))

        time.sleep(0.1)
        timers.tick()

        self.assertEqual(2, mock.call_count)



    def test_call_all_timers(self):
        mock = unittest.mock.Mock()
        timers = timer.Timers()
        for interval in [0, 0, 0]:
            timers.add(timer.Timer(interval, lambda: mock()))

        time.sleep(0.1)
        timers.tick()

        self.assertTrue(timers.empty())
        self.assertEqual(3, mock.call_count)

    def test_call_one_timer(self):
        mock = unittest.mock.Mock()
        timers = timer.Timers()
        for interval in [3, 0, 4]:
            timers.add(timer.Timer(interval, lambda: mock()))

        time.sleep(0.1)
        timers.tick()

        self.assertFalse(timers.empty())
        self.assertEqual(1, mock.call_count)
        self.assertEqual(2, len(timers.timers))
        self.assertEqual(2, len(timers.schedule))

    def test_eager_call_of_timers(self):
        mock = unittest.mock.Mock()
        timers = timer.Timers()
        for interval in [10, 5, 3]:
            timers.add(timer.Timer(interval, lambda: mock()))

        timers.tick()

        self.assertFalse(timers.empty())
        self.assertEqual(0, mock.call_count)

    def test_empty(self):
        timers = timer.Timers()
        self.assertTrue(timers.empty())

    def test_add_timer(self):
        timers = timer.Timers()
        for interval in range(2, 5):
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
