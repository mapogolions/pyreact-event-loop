import io
import os
import pytest
import signal
import socket
import time
import unittest

import tests.testkit as testkit


def test_loop_without_resources(loop):
    testkit.assert_run_faster_than(loop, 0.02)


def test_future_tick_handler_can_cancel_registered_stream(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], mock)
    loop.future_tick(lambda: loop.remove_write_stream(socket_pair[1]))
    loop.run()
    mock.assert_not_called()


def test_add_write_stream_ignore_second_callable(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], lambda stream: mock(1))
    loop.add_write_stream(socket_pair[1], lambda stream: mock(2))
    testkit.next_tick(loop)
    assert mock.call_args_list == [unittest.mock.call(1)]


def test_add_read_stream_ignore_second_callable(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], lambda stream: mock(stream.recv(20)))
    loop.add_read_stream(socket_pair[0], lambda stream: mock(2))
    socket_pair[1].send(b"foo")
    testkit.next_tick(loop)
    socket_pair[1].send(b"bar")
    testkit.next_tick(loop)
    expected = [unittest.mock.call(b"foo"), unittest.mock.call(b"bar")]
    assert mock.call_args_list == expected


def test_add_write_stream(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], mock)
    testkit.next_tick(loop)
    testkit.next_tick(loop)
    assert mock.call_count == 2


def test_add_read_stream(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], mock)
    socket_pair[1].send(b"hello")
    testkit.next_tick(loop)
    socket_pair[1].send(b"world")
    testkit.next_tick(loop)
    assert mock.call_count == 2


def test_select_loop_timeout_emulation(loop, mock):
    loop.add_timer(0.05, mock)
    start = time.time()
    loop.run()
    interval = time.time() - start
    mock.assert_called_once()
    assert interval >= 0.04


def test_periodic_timer(loop, mock):
    timer = loop.add_periodic_timer(0.05, mock)
    loop.add_timer(0.12, lambda: loop.cancel_timer(timer))
    loop.run()
    assert mock.call_count == 2


def test_remove_read_stream_instantly(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], mock)
    loop.remove_read_stream(socket_pair[0])
    socket_pair[1].send(b"bar")
    testkit.next_tick(loop)
    mock.assert_not_called()


def test_remove_write_stream_instantly(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], mock)
    loop.remove_write_stream(socket_pair[1])
    testkit.next_tick(loop)
    mock.assert_not_called()


def test_remove_read_stream_after_reading(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], mock)
    socket_pair[1].send(b"foo")
    testkit.next_tick(loop)
    loop.remove_read_stream(socket_pair[0])
    socket_pair[1].send(b"bar")
    testkit.next_tick(loop)
    mock.assert_called_once()


def test_remove_write_stream_after_writing(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], mock)
    testkit.next_tick(loop)
    loop.remove_write_stream(socket_pair[1])
    testkit.next_tick(loop)
    mock.assert_called_once()


def test_read_stream_removes_itself(loop, mock, socket_pair):
    def remove_itself(stream):
        mock(len(loop.read_streams))
        loop.remove_read_stream(stream)
        mock(len(loop.read_streams))

    loop.add_read_stream(socket_pair[0], remove_itself)
    socket_pair[1].send(b"hello")
    loop.run()
    expected = [unittest.mock.call(1), unittest.mock.call(0)]
    assert mock.call_args_list == expected


def test_write_stream_removes_itself(loop, mock, socket_pair):
    def remove_itself(stream):
        mock(len(loop.write_streams))
        loop.remove_write_stream(stream)
        mock(len(loop.write_streams))

    loop.add_write_stream(socket_pair[1], remove_itself)
    loop.run()
    expected = [unittest.mock.call(1), unittest.mock.call(0)]
    assert mock.call_args_list == expected


def test_cleanup_before_mock_call(loop, mock, socket_pair):
    def cleanup(stream):
        loop.remove_read_stream(stream)
        loop.remove_write_stream(stream)

    loop.add_read_stream(socket_pair[0], mock)
    loop.add_write_stream(socket_pair[0], cleanup)
    mock.assert_not_called()


def test_sends_message_to_the_read_stream_implicitly(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], mock)
    socket_pair[1].close()
    testkit.next_tick(loop)
    mock.assert_called_once()


def test_future_tick_event_generated_by_future_tick(loop, mock):
    loop.future_tick(lambda: loop.future_tick(mock))
    loop.run()
    mock.assert_called_once()


def test_future_tick_event_generated_by_timer(loop, mock):
    loop.add_timer(0.01, lambda: loop.future_tick(mock))
    loop.run()
    mock.assert_called_once()

def test_future_tick(loop, mock):
    loop.future_tick(lambda: mock(1))
    loop.future_tick(lambda: mock(2))
    loop.run()
    expected = [unittest.mock.call(1), unittest.mock.call(2)]
    assert mock.call_args_list == expected


def test_future_tick_fires_before_IO(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], lambda stream: mock("io"))
    loop.future_tick(lambda: mock("tick"))
    testkit.next_tick(loop)
    expected = [unittest.mock.call("tick"), unittest.mock.call("io")]
    assert mock.call_args_list == expected


def test_future_tick_fires_before_timers(loop, mock):
    loop.add_timer(0, lambda: mock("timer 1"))
    loop.add_timer(0.03, lambda: mock("timer 2"))
    loop.add_timer(0, lambda: mock("timer 3"))
    loop.future_tick(lambda: mock("tick 1"))
    loop.future_tick(lambda: mock("tick 2"))
    loop.run()
    expected = [unittest.mock.call("tick 1"),
                unittest.mock.call("tick 2"),
                unittest.mock.call("timer 1"),
                unittest.mock.call("timer 3"),
                unittest.mock.call("timer 2")]
    assert mock.call_args_list == expected


def test_listening_to_closed_read_stream(loop, mock, socket_pair):
    socket_pair[0].close()
    with pytest.raises(Exception):
        loop.add_read_stream(socket_pair[0], mock)


def test_listening_to_closed_write_stream(loop, mock, socket_pair):
    socket_pair[1].close()
    with pytest.raises(Exception):
        loop.add_write_stream(socket_pair[1], mock)


def test_read_only_stream_is_listened_as_writable(loop, mock, socket_pair):
    read_only = socket.SocketIO(socket_pair[0], 'rb')
    assert read_only.readable()
    assert not read_only.writable()
    loop.add_write_stream(read_only, mock)
    testkit.next_tick(loop)
    mock.assert_called_once()


def test_write_only_strem_is_listened_as_readable(loop, mock, socket_pair):
    write_only = socket.SocketIO(socket_pair[0], 'wb')
    assert not write_only.readable()
    assert write_only.writable()
    loop.add_read_stream(write_only, mock)
    socket_pair[1].send(b"foo")
    testkit.next_tick(loop)
    mock.assert_called_once()


def test_attempt_to_write_to_the_read_only_stream(loop, mock, socket_pair):
    read_only = socket.SocketIO(socket_pair[0], 'rb')

    def collapse(stream):
        try:
            mock()
            stream.write(b"foo")
            mock()
        except io.UnsupportedOperation:
            pass

    loop.add_write_stream(read_only, collapse)
    testkit.next_tick(loop)
    mock.assert_called_once()


def test_attempt_to_read_from_the_write_only_stream(loop, mock, socket_pair):
    write_only = socket.SocketIO(socket_pair[0], 'wb')

    def collapse(stream):
        try:
            mock()
            stream.read(10)
            mock()
        except io.UnsupportedOperation:
            pass

    loop.add_read_stream(write_only, collapse)
    socket_pair[1].send(b"bar")
    testkit.next_tick(loop)
    mock.assert_called_once()


def test_timer_inteval_can_be_far_in_future(loop, mock):
    timer = loop.add_timer(10 ** 6, mock)
    loop.future_tick(lambda: loop.cancel_timer(timer))
    testkit.assert_run_faster_than(loop, 0.02)


def test_signals_are_not_handled_without_the_running_loop(loop, mock):
    loop.add_signal(signal.SIGUSR1, mock)
    os.kill(os.getpid(), signal.SIGUSR1)
    mock.assert_not_called()


def test_many_handlers_per_signal(loop, mock):
    loop.add_signal(signal.SIGUSR2, lambda *args: mock())
    loop.add_signal(signal.SIGUSR2, lambda *args: mock())
    os.kill(os.getpid(), signal.SIGUSR2)
    testkit.next_tick(loop)
    assert mock.call_count == 2


def test_signal_multiple_usages_for_the_same_listener(loop, mock):
    loop.add_signal(signal.SIGHUP, mock)
    loop.add_signal(signal.SIGHUP, mock)
    os.kill(os.getpid(), signal.SIGHUP)
    testkit.next_tick(loop)
    mock.assert_called_once()
