import unittest
import unittest.mock

from loop.tick import FutureTickQueue


class TestTick(unittest.TestCase):
    def test_tick_queue_is_empty(self):
        queue = FutureTickQueue()
        self.assertIs(True, queue.empty())

    def test_add_item_to_tick_queue(self):
        queue = FutureTickQueue()
        queue.add(lambda: None)
        self.assertIs(False, queue.empty())

    def test_call_tick(self):
        mock = unittest.mock.Mock()
        queue = FutureTickQueue()
        queue.add(lambda: mock("first"))
        queue.add(lambda: mock("second"))
        queue.add(lambda: mock("third"))
        queue.tick()
        self.assertEqual(3, mock.call_count)
        self.assertEqual(unittest.mock.call("third"), mock.call_args)
        self.assertIs(True, queue.empty())
