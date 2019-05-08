import abc
import socket
import time
import unittest


class TestAbstractLoop(abc.ABC):
    def test_loop_without_resources(self):
        self.assert_run_faster_than(0.02)

    def test_future_tick_handler_can_cancel_registered_stream(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        rstream, wstream = self.create_socket_pair()
        loop.add_write_stream(wstream, mock)
        loop.future_tick(
            lambda *args: loop.remove_write_stream(wstream)
        )
        loop.run()
        self.close_sockets(rstream, wstream)
        mock.assert_not_called()

    def test_add_write_stream_ignore_second_callable(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        rstream, wstream = self.create_socket_pair()
        loop.add_write_stream(wstream, lambda stream: mock(1))
        loop.add_write_stream(wstream, lambda stream: mock(2))
        self.next_tick(loop)
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(1)],
            mock.call_args_list
        )

    def test_add_read_stream_ignore_second_callable(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        rstream, wstream = self.create_socket_pair()
        loop.add_read_stream(
            rstream,
            lambda stream: mock(stream.recv(1024))
        )
        loop.add_read_stream(rstream, lambda stream: mock(2))
        wstream.send(b"hello")
        self.next_tick(loop)
        wstream.send(b"world")
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        self.assertEqual(
            [unittest.mock.call(b"hello"), unittest.mock.call(b"world")],
            mock.call_args_list
        )

    def test_add_write_stream(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        rstream, wstream = self.create_socket_pair()
        loop.add_write_stream(wstream, mock)
        self.next_tick(loop)
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        self.assertEqual(2, mock.call_count)

    def test_add_read_stream(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        rstream, wstream = self.create_socket_pair()
        loop.add_read_stream(rstream, mock)
        wstream.send(b"hello")
        self.next_tick(loop)
        wstream.send(b"world")
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        self.assertEqual(2, mock.call_count)

    def test_select_loop_timeout_emulation(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        loop.add_timer(0.05, mock)
        start = time.time()
        loop.run()
        interval = time.time() - start
        mock.assert_called_once()
        self.assertLessEqual(0.04, interval)

    def test_periodic_timer(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        timer = loop.add_periodic_timer(0.05, mock)
        loop.add_timer(0.12, lambda: loop.cancel_timer(timer))
        loop.run()
        self.assertEqual(2, mock.call_count)

    def test_remove_read_stream_instantly(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()
        loop.add_read_stream(rstream, mock)
        loop.remove_read_stream(rstream)
        wstream.send(b"bar")
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        mock.assert_not_called()

    def test_remove_read_stream_after_reading(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()
        loop.add_read_stream(rstream, mock)
        wstream.send(b"foo")
        self.next_tick(loop)
        loop.remove_read_stream(rstream)
        wstream.send(b"bar")
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        mock.assert_called_once()

    def test_remove_write_stream_instantly(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()
        loop.add_write_stream(wstream, mock)
        loop.remove_write_stream(wstream)
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        mock.assert_not_called()

    def test_remove_write_stream_after_writing(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()
        loop.add_write_stream(wstream, mock)
        self.next_tick(loop)
        loop.remove_write_stream(wstream)
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        mock.assert_called_once()

    def test_read_stream_removes_itself(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()

        def remove_itself(stream):
            nonlocal loop, mock
            mock(len(loop.read_streams))
            loop.remove_read_stream(stream)
            mock(len(loop.read_streams))

        loop.add_read_stream(rstream, remove_itself)
        wstream.send(b"hello")
        loop.run()
        self.close_sockets(rstream, wstream)
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(0)],
            mock.call_args_list
        )

    def test_write_stream_removes_itself(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()

        def remove_itself(stream):
            nonlocal loop, mock
            mock(len(loop.write_streams))
            loop.remove_write_stream(stream)
            mock(len(loop.write_streams))

        loop.add_write_stream(wstream, remove_itself)
        loop.run()
        self.close_sockets(rstream, wstream)
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(0)],
            mock.call_args_list
        )

    def test_cleanup_before_mock_call(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()

        def cleanup(stream):
            nonlocal loop
            loop.remove_read_stream(stream)
            loop.remove_write_stream(stream)

        loop.add_read_stream(rstream, mock)
        loop.add_write_stream(rstream, cleanup)
        self.close_sockets(rstream, wstream)
        self.assert_run_faster_than(0.02)
        mock.assert_not_called()

    def test_call_of_the_close_sends_message_to_read_stream_implicitly(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        rstream, wstream = self.create_socket_pair()
        loop.add_read_stream(rstream, mock)
        wstream.close()
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        mock.assert_called_once()


    def test_read_streams_are_handled_earlier_than_write_streams(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        stream, another = self.create_socket_pair()

        def cleanup(stream):
            nonlocal loop, mock
            mock("write")
            loop.remove_read_stream(stream)
            loop.remove_write_stream(stream)
            stream.close()

        loop.add_read_stream(stream, lambda *args: mock("read"))
        loop.add_write_stream(stream, cleanup)
        another.close()
        loop.run()
        self.close_sockets(stream, another)
        self.assertEqual(
            [unittest.mock.call("read"), unittest.mock.call("write")],
            mock.call_args_list
        )

    def test_future_tick_event_generated_by_future_tick(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        loop.future_tick(lambda *args: loop.future_tick(mock))
        loop.run()
        mock.assert_called_once()

    def test_future_tick_event_generated_by_timer(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        loop.add_timer(
            0.01,
            lambda *args: loop.future_tick(mock)
        )
        loop.run()
        mock.assert_called_once()

    def test_future_tick(self):
        mock = unittest.mock.Mock()
        loop = self.create_event_loop()
        loop.future_tick(lambda: mock(1))
        loop.future_tick(lambda: mock(2))
        loop.run()
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(2)],
            mock.call_args_list
        )

    def test_future_tick_fires_before_IO(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        stream, another = self.create_socket_pair()
        loop.add_write_stream(stream, lambda stream: mock("io"))
        loop.future_tick(lambda *args: mock("tick"))
        self.next_tick(loop)
        self.close_sockets(stream, another)
        self.assertEqual(
            [unittest.mock.call("tick"), unittest.mock.call("io")],
            mock.call_args_list
        )

    def test_future_tick_fires_before_timers(self):
        loop = self.create_event_loop()
        mock = unittest.mock.Mock()
        loop.add_timer(0, lambda *args: mock("timer 1"))
        loop.add_timer(0.03, lambda *args: mock("timer 2"))
        loop.add_timer(0, lambda *args: mock("timer 3"))
        loop.future_tick(lambda *args: mock("tick 1"))
        loop.future_tick(lambda *ars: mock("tick 2"))
        loop.run()
        self.assertEqual(
            [unittest.mock.call("tick 1"),
             unittest.mock.call("tick 2"),
             unittest.mock.call("timer 1"),
             unittest.mock.call("timer 3"),
             unittest.mock.call("timer 2")],
            mock.call_args_list
        )

    @abc.abstractmethod
    def assertEqual(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def assertLess(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def assertLessEqual(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def assertGreater(self, *args, **kwargs):
        pass

    @abc.abstractstaticmethod
    def create_event_loop():
        pass

    @staticmethod
    def create_socket_pair():
        rstream, wstream = socket.socketpair(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP
        )
        rstream.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
        wstream.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
        rstream.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
        wstream.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
        rstream.setblocking(False)
        wstream.setblocking(False)
        return (rstream, wstream)

    @staticmethod
    def close_sockets(*resources):
        for resource in resources:
            resource.close()

    @staticmethod
    def next_tick(event_loop):
        event_loop.future_tick(lambda *args: event_loop.stop())
        event_loop.run()

    def assert_run_slower_than(self, min_interval):
        event_loop = self.create_event_loop()
        start = time.time()
        event_loop.run()
        interval = time.time() - start
        self.assertGreater(interval, min_interval)

    def assert_run_faster_than(self, max_interval):
        event_loop = self.create_event_loop()
        start = time.time()
        event_loop.run()
        interval = time.time() - start
        self.assertLess(interval, max_interval)
