import socket
import time


def assert_run_faster_than(loop, max_interval):
    start = time.time()
    loop.run()
    interval = time.time() - start
    assert interval < max_interval


def assert_run_slower_than(loop, min_interval):
    start = time.time()
    loop.run()
    interval = time.time() - start
    assert interval > min_interval


def create_socket_pair():
    first, second = socket.socketpair(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
        socket.IPPROTO_IP
    )
    first.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
    second.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
    first.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
    second.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
    first.setblocking(False)
    second.setblocking(False)
    return (first, second)
