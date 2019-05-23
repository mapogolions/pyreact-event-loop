import pytest
import unittest.mock

import tests.testkit as testkit


@pytest.fixture
def socket_pair():
    streams = testkit.create_socket_pair()
    yield streams
    for stream in streams:
        stream.close()


@pytest.fixture
def mock():
    return unittest.mock.Mock()


@pytest.fixture
def tick_timeout():
    return 0.02
