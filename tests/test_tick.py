import unittest
import unittest.mock

from loop.tick import FutureTickQueue


class TestTick(unittest.TestCase):
    def setUp(self):
        self.queue = FutureTickQueue()

    def test_tick_queue_is_empty(self):
        self.assertIs(True, self.queue.empty())

    def test_add_item_to_tick_queue(self):
        self.queue.add(lambda: None)
        self.assertIs(False, self.queue.empty())

    def test_call_tick(self):
        mock = unittest.mock.Mock()
        self.queue.add(lambda: mock("first"))
        self.queue.add(lambda: mock("second"))
        self.queue.add(lambda: mock("third"))
        self.queue.tick()
        self.assertEqual(3, mock.call_count)
        self.assertEqual(unittest.mock.call("third"), mock.call_args)
        self.assertIs(True, self.queue.empty())
