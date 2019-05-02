import unittest
import unittest.mock

import loop.timer as timer


class TestTimer(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
