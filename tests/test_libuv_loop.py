import pytest
import unittest

import event_loop
import tests.testkit as testkit
from tests.loop_test_case import *


@pytest.fixture
def loop():
    return event_loop.LibuvLoop()


def test_read_io_fires_before_write_io_on_different_sockets(loop, mock, socket_pair):
    loop.add_read_stream(socket_pair[0], lambda stream: mock("read"))
    loop.add_write_stream(socket_pair[1], lambda stream: mock("write"))
    socket_pair[1].send(b"bar")
    testkit.next_tick(loop)
    expected = [unittest.mock.call("read"), unittest.mock.call("write")]
    assert mock.call_args_list == expected


def test_read_io_and_write_io_on_the_same_socket(loop, mock, socket_pair):
    the_same, another = socket_pair
    loop.add_read_stream(the_same, lambda stream: mock("read"))
    loop.add_write_stream(the_same, lambda stream: mock("write"))
    another.send(b"bar")
    testkit.next_tick(loop)
    expected = [unittest.mock.call("write")]
    assert mock.call_args_list == expected
