import socket
import time
import unittest
import unittest.mock

from loop.select_loop import SelectLoop
from loop.timer import Timers
from loop.signal import Signals
from loop.tick import FutureTickQueue


class TestSelectLoop(unittest.TestCase):
    def setUp(self):
        self.event_loop = SelectLoop()
        self.mock = unittest.mock.Mock()
        (self.rstream, self.wstream) = self.create_socket_pair()

    def tearDown(self):
        self.rstream.close()
        self.wstream.close()

    def create_socket_pair(self):
        rstream, wstream = socket.socketpair(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP
        )
        rstream.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
        wstream.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
        rstream.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
        wstream.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
        return (rstream, wstream)

    def next_tick(self):
        self.event_loop.future_tick(lambda: self.event_loop.stop())
        self.event_loop.run()

    def test_add_read_stream_ignore_second_callable(self):
        self.event_loop.add_read_stream(self.rstream, lambda stream: self.mock(1))
        self.event_loop.add_read_stream(self.rstream, lambda stream: self.mock("ignore"))

        self.wstream.send(b"hello")
        self.next_tick()

        self.wstream.send(b"world")
        self.next_tick()

        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(1)],
            self.mock.call_args_list
        )

    def test_add_write_stream(self):
        self.event_loop.add_write_stream(self.wstream, self.mock)
        self.next_tick()
        self.next_tick()

        self.assertEqual(2, self.mock.call_count)

    def test_add_read_stream(self):
        self.event_loop.add_read_stream(self.rstream, self.mock)
        self.wstream.send(b"hello")
        self.next_tick()
        self.wstream.send(b"world")
        self.next_tick()

        self.assertEqual(2, self.mock.call_count)

    def test_select_loop_timeout_emulation(self):
        self.event_loop.add_timer(0.05, self.mock)

        start = time.time()
        self.event_loop.run()
        end = time.time()
        interval = end - start

        self.mock.assert_called_once()
        self.assertLessEqual(0.04, interval)

    def test_periodic_timer(self):
        timer = self.event_loop.add_periodic_timer(0.05, self.mock)
        self.event_loop.add_timer(0.12, lambda: self.event_loop.cancel_timer(timer))
        self.event_loop.run()

        self.assertEqual(2, self.mock.call_count)

    def test_future_tick(self):
        self.event_loop.future_tick(lambda: self.mock(1))
        self.event_loop.future_tick(lambda: self.mock(2))
        self.event_loop.run()

        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(2)],
            self.mock.call_args_list
        )

    def test_fututre_tick_earlier_than_timers(self):
        self.event_loop.add_timer(0, lambda: self.mock("timer 1"))
        self.event_loop.add_timer(0.03, lambda: self.mock("timer 2"))
        self.event_loop.add_timer(0, lambda: self.mock("timer 3"))
        self.event_loop.future_tick(lambda: self.mock("tick 1"))
        self.event_loop.future_tick(lambda: self.mock("tick 2"))
        self.event_loop.run()

        self.assertEqual(
            [unittest.mock.call("tick 1"),
             unittest.mock.call("tick 2"),
             unittest.mock.call("timer 1"),
             unittest.mock.call("timer 3"),
             unittest.mock.call("timer 2")],
            self.mock.call_args_list
        )
