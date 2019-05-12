import unittest

from tests.test_abstract_loop import TestAbstractLoop
from loop.libuv_loop import LibuvLoop


class TestLibuvLoop(unittest.TestCase, TestAbstractLoop):
    @staticmethod
    def create_event_loop():
        return LibuvLoop()
