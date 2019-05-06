import socket
import time
import unittest
import unittest.mock

from loop.select_loop import SelectLoop


class TestSelectLoop(unittest.TestCase):
    def setUp(self):
        self.loop = SelectLoop()
        self.mock = unittest.mock.Mock()
        (self.rstream, self.wstream) = self.create_socket_pair()

    def tearDown(self):
        self.rstream.close()
        self.wstream.close()

    def test_future_tick_handler_can_cancel_registered_stream(self):
        self.loop.add_write_stream(self.wstream, self.mock)
        self.loop.future_tick(
            lambda: self.loop.remove_write_stream(self.wstream)
        )
        self.loop.run()

        self.mock.assert_not_called()

    def test_loop_without_resources(self):
        self.assert_run_faster_than(0.02)

    def test_add_write_stream_ignore_second_callable(self):
        self.loop.add_write_stream(self.wstream, lambda stream: self.mock(1))
        self.loop.add_write_stream(self.wstream, lambda stream: self.mock("ignore"))
        self.next_tick()
        self.next_tick()

        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(1)],
            self.mock.call_args_list
        )

    def test_add_read_stream_ignore_second_callable(self):
        self.loop.add_read_stream(
            self.rstream,
            lambda stream: self.mock(stream.recv(1024))
        )
        self.loop.add_read_stream(self.rstream, lambda stream: self.mock("ignore"))

        self.wstream.send(b"hello")
        self.next_tick()

        self.wstream.send(b"world")
        self.next_tick()

        self.assertEqual(
            [unittest.mock.call(b"hello"), unittest.mock.call(b"world")],
            self.mock.call_args_list
        )

    def test_add_write_stream(self):
        self.loop.add_write_stream(self.wstream, self.mock)
        self.next_tick()
        self.next_tick()

        self.assertEqual(2, self.mock.call_count)

    def test_add_read_stream(self):
        self.loop.add_read_stream(self.rstream, self.mock)
        self.wstream.send(b"hello")
        self.next_tick()
        self.wstream.send(b"world")
        self.next_tick()

        self.assertEqual(2, self.mock.call_count)

    def test_select_loop_timeout_emulation(self):
        self.loop.add_timer(0.05, self.mock)
        start = time.time()
        self.loop.run()
        end = time.time()
        interval = end - start

        self.mock.assert_called_once()
        self.assertLessEqual(0.04, interval)

    def test_periodic_timer(self):
        timer = self.loop.add_periodic_timer(0.05, self.mock)
        self.loop.add_timer(0.12, lambda: self.loop.cancel_timer(timer))
        self.loop.run()

        self.assertEqual(2, self.mock.call_count)

    def test_future_tick(self):
        self.loop.future_tick(lambda: self.mock(1))
        self.loop.future_tick(lambda: self.mock(2))
        self.loop.run()

        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(2)],
            self.mock.call_args_list
        )

    def test_fututre_tick_earlier_than_timers(self):
        self.loop.add_timer(0, lambda: self.mock("timer 1"))
        self.loop.add_timer(0.03, lambda: self.mock("timer 2"))
        self.loop.add_timer(0, lambda: self.mock("timer 3"))
        self.loop.future_tick(lambda: self.mock("tick 1"))
        self.loop.future_tick(lambda: self.mock("tick 2"))
        self.loop.run()

        self.assertEqual(
            [unittest.mock.call("tick 1"),
             unittest.mock.call("tick 2"),
             unittest.mock.call("timer 1"),
             unittest.mock.call("timer 3"),
             unittest.mock.call("timer 2")],
            self.mock.call_args_list
        )

    def test_remove_read_stream_instantly(self):
        self.loop.add_read_stream(self.rstream, self.mock)
        self.loop.remove_read_stream(self.rstream)
        self.wstream.send(b"bar")
        self.next_tick()

        self.mock.assert_not_called()

    def test_remove_read_stream_after_reading(self):
        self.loop.add_read_stream(self.rstream, self.mock)
        self.wstream.send(b"foo")
        self.next_tick()
        self.loop.remove_read_stream(self.rstream)
        self.wstream.send(b"bar")
        self.next_tick()

        self.mock.assert_called_once()

    def test_remove_write_stream_instantly(self):
        self.loop.add_write_stream(self.wstream, self.mock)
        self.loop.remove_write_stream(self.wstream)
        self.next_tick()

        self.mock.assert_not_called()

    def test_remove_write_stream_after_writing(self):
        self.loop.add_write_stream(self.wstream, self.mock)
        self.next_tick()
        self.loop.remove_write_stream(self.wstream)
        self.next_tick()

        self.mock.assert_called_once()

    def test_read_stream_removes_itself(self):
        def remove_itself(stream):
            self.mock(len(self.loop.read_streams))
            self.loop.remove_read_stream(stream)
            self.mock(len(self.loop.read_streams))

        self.loop.add_read_stream(self.rstream, remove_itself)
        self.wstream.send(b"hello")
        self.loop.run()

        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(0)],
            self.mock.call_args_list
        )

    def test_write_stream_removes_itself(self):
        def remove_itself(stream):
            self.mock(len(self.loop.write_streams))
            self.loop.remove_write_stream(stream)
            self.mock(len(self.loop.write_streams))

        self.loop.add_write_stream(self.wstream, remove_itself)
        self.loop.run()

        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(0)],
            self.mock.call_args_list
        )

    def test_without_called(self):
        def cleanup(stream):
            self.loop.remove_read_stream(stream)
            self.loop.remove_write_stream(stream)

        self.loop.add_read_stream(self.rstream, self.mock)
        self.loop.add_write_stream(self.rstream, cleanup)

        self.assert_run_faster_than(0.02)
        self.mock.assert_not_called()

    def test_call_of_the_close_sends_message_to_read_stream_implicitly(self):
        self.loop.add_read_stream(self.rstream, self.mock)
        self.wstream.close()
        self.next_tick()

        self.mock.assert_called_once()

    def test_read_streams_are_handled_earlier_than_write_streams(self):
        def cleanup(stream):
            self.mock("write")
            self.loop.remove_read_stream(stream)
            self.loop.remove_write_stream(stream)
            stream.close()

        stream, another = self.create_socket_pair()
        self.loop.add_read_stream(stream, lambda _: self.mock("read"))
        self.loop.add_write_stream(stream, cleanup)
        another.close()
        self.loop.run()

        self.assertEqual(
            [unittest.mock.call("read"), unittest.mock.call("write")],
            self.mock.call_args_list
        )


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
        self.loop.future_tick(lambda: self.loop.stop())
        self.loop.run()

    def assert_run_slower_than(self, min_interval):
        start = time.time()
        self.loop.run()
        interval = time.time() - start
        self.assertGreater(interval, min_interval)

    def assert_run_faster_than(self, max_interval):
        start = time.time()
        self.loop.run()
        interval = time.time() - start
        self.assertLess(interval, max_interval)
