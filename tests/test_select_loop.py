import unittest

from loop.select_loop import SelectLoop
from tests.test_abstract_loop import TestAbstractLoop


class TestSelectLoop(unittest.TestCase, TestAbstractLoop):
    @staticmethod
    def create_event_loop():
        return SelectLoop()

    def test_read_earlier_than_write_on_different_sockets(self):
        loop, mock = self.create_event_loop(), unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()
        loop.add_read_stream(rstream, lambda stream: mock("read"))
        loop.add_write_stream(wstream, lambda stream: mock("write"))
        wstream.send(b"bar")
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        self.assertEqual(
            [unittest.mock.call("read"), unittest.mock.call("write")],
            mock.call_args_list
        )

    def test_read_and_write_on_the_same_socket(self):
        loop, mock = self.create_event_loop(), unittest.mock.Mock()
        the_same, another = self.create_socket_pair()
        loop.add_read_stream(the_same, lambda stream: mock("read"))
        loop.add_write_stream(the_same, lambda stream: mock("write"))
        another.send(b"bar")
        self.next_tick(loop)
        self.close_sockets(the_same, another)
        self.assertEqual(
            [unittest.mock.call("read"), unittest.mock.call("write")],
            mock.call_args_list
        )
