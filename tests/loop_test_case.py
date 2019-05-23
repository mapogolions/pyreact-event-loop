import io
import os
import pytest
import signal
import socket
import time
import unittest

import tests.testkit as testkit


def test_loop_without_resources(loop, tick_timeout):
    testkit.assert_run_faster_than(loop, tick_timeout)


def test_future_tick_handler_can_cancel_registered_stream(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], mock)
    loop.future_tick(lambda: loop.remove_write_stream(socket_pair[1]))
    loop.run()
    mock.assert_not_called()


def test_add_write_stream_ignore_second_callable(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], lambda stream: mock(1))
    loop.add_write_stream(socket_pair[1], lambda stream: mock(2))
    loop.next_tick()
    assert mock.call_args_list == [unittest.mock.call(1)]


def test_add_read_stream_ignore_second_callable(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], lambda stream: mock(stream.recv(20)))
    loop.add_read_stream(socket_pair[0], lambda stream: mock(2))
    socket_pair[1].send(b"foo")
    loop.next_tick()
    socket_pair[1].send(b"bar")
    loop.next_tick()
    expected = [unittest.mock.call(b"foo"), unittest.mock.call(b"bar")]
    assert mock.call_args_list == expected


def test_add_write_stream(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], mock)
    loop.next_tick()
    loop.next_tick()
    assert mock.call_count == 2


def test_add_read_stream(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], mock)
    socket_pair[1].send(b"hello")
    loop.next_tick()
    socket_pair[1].send(b"world")
    loop.next_tick()
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
    loop.next_tick()
    mock.assert_not_called()


def test_remove_write_stream_instantly(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], mock)
    loop.remove_write_stream(socket_pair[1])
    loop.next_tick()
    mock.assert_not_called()


def test_remove_read_stream_after_reading(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], mock)
    socket_pair[1].send(b"foo")
    loop.next_tick()
    loop.remove_read_stream(socket_pair[0])
    socket_pair[1].send(b"bar")
    loop.next_tick()
    mock.assert_called_once()


def test_remove_stream_for_read_only(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], lambda stream: mock("read"))
    loop.add_write_stream(socket_pair[1], lambda stream: mock("write"))
    loop.remove_read_stream(socket_pair[0])
    socket_pair[1].send(b"foo")
    loop.next_tick()
    assert mock.call_args_list == [unittest.mock.call("write")]


def test_remove_stream_for_write_only(loop, mock, socket_pair):
    socket_pair[1].send(b"bar")
    loop.add_read_stream(socket_pair[0], lambda stream: mock("read"))
    loop.add_write_stream(socket_pair[1], lambda stream: mock("write"))
    loop.remove_write_stream(socket_pair[1])
    loop.next_tick()
    assert mock.call_args_list == [unittest.mock.call("read")]


def test_remove_write_stream_after_writing(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], mock)
    loop.next_tick()
    loop.remove_write_stream(socket_pair[1])
    loop.next_tick()
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


def test_sends_message_to_the_read_stream_implicitly(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], mock)
    socket_pair[1].close()  # implicitly
    loop.next_tick()
    mock.assert_called_once()


def test_stop_should_prevent_run_from_blocking(loop, mock, tick_timeout):
    loop.add_timer(3, mock)
    loop.future_tick(loop.stop)
    testkit.assert_run_faster_than(loop, tick_timeout * 2)
    mock.assert_not_called()


def test_run_waits_for_future_tick_events(loop, mock, socket_pair):
    def handle(stream):
        loop.remove_write_stream(stream)
        loop.future_tick(mock)

    loop.add_write_stream(socket_pair[0], handle)
    loop.run()
    mock.not_called_called()


def test_future_tick(loop, mock):
    loop.future_tick(lambda: mock(1))
    loop.future_tick(lambda: mock(2))
    loop.run()
    expected = [unittest.mock.call(1), unittest.mock.call(2)]
    assert mock.call_args_list == expected


def test_handle_available_io_between_ticks(loop, mock, socket_pair):
    def handle_write_stream(stream):
        mock("stream")
        loop.remove_write_stream(stream)

    def rec_future_tick():
        mock(1)
        loop.future_tick(lambda *args: mock(2))

    loop.add_write_stream(socket_pair[1], handle_write_stream)
    loop.future_tick(rec_future_tick)
    loop.run()
    expected = [unittest.mock.call(1),
                unittest.mock.call("stream"),
                unittest.mock.call(2)]
    assert mock.call_args_list == expected


def test_future_tick_event_generated_by_future_tick(loop, mock):
    loop.future_tick(lambda: loop.future_tick(mock))
    loop.run()
    mock.assert_called_once()


def test_future_tick_event_generated_by_timer(loop, mock):
    loop.add_timer(0.01, lambda: loop.future_tick(mock))
    loop.run()
    mock.assert_called_once()


def test_future_tick_fires_before_IO(loop, mock, socket_pair):
    loop.add_write_stream(socket_pair[1], lambda stream: mock("io"))
    loop.future_tick(lambda: mock("tick"))
    loop.next_tick()
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
    loop.next_tick()
    mock.assert_called_once()


def test_write_only_stream_is_listened_as_readable(loop, mock, socket_pair):
    write_only = socket.SocketIO(socket_pair[0], 'wb')
    assert not write_only.readable()
    assert write_only.writable()
    loop.add_read_stream(write_only, mock)
    socket_pair[1].send(b"foo")
    loop.next_tick()
    mock.assert_called_once()


def test_write_to_the_read_only_stream(loop, mock, socket_pair):
    read_only = socket.SocketIO(socket_pair[0], 'rb')

    def collapse(stream):
        try:
            stream.write(b"foo")
        except io.UnsupportedOperation:
            mock()

    loop.add_write_stream(read_only, collapse)
    loop.next_tick()
    mock.assert_called_once()


def test_read_from_the_write_only_stream(loop, mock, socket_pair):
    write_only = socket.SocketIO(socket_pair[0], 'wb')

    def collapse(stream):
        try:
            stream.read(10)
        except io.UnsupportedOperation:
            mock()

    loop.add_read_stream(write_only, collapse)
    socket_pair[1].send(b"bar")
    loop.next_tick()
    mock.assert_called_once()


def test_timer_inteval_can_be_far_in_future(loop, mock, tick_timeout):
    timer = loop.add_timer(10 ** 6, mock)
    loop.future_tick(lambda: loop.cancel_timer(timer))
    testkit.assert_run_faster_than(loop, tick_timeout)


def test_signals_are_not_handled_without_the_running_loop(loop, mock):
    loop.add_signal(signal.SIGUSR1, mock)
    os.kill(os.getpid(), signal.SIGUSR1)
    mock.assert_not_called()


def test_many_handlers_per_signal(loop, mock):
    loop.add_signal(signal.SIGUSR2, lambda *args: mock())
    loop.add_signal(signal.SIGUSR2, lambda *args: mock())
    os.kill(os.getpid(), signal.SIGUSR2)
    loop.next_tick()
    assert mock.call_count == 2


def test_signal_multiple_usages_for_the_same_listener(loop, mock):
    loop.add_signal(signal.SIGHUP, mock)
    loop.add_signal(signal.SIGHUP, mock)
    os.kill(os.getpid(), signal.SIGHUP)
    loop.next_tick()
    mock.assert_called_once()
