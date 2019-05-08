import unittest

from loop.libev_loop import LibevLoop
from tests.test_abstract_loop import TestAbstractLoop


class TestLibevLoop(unittest.TestCase, TestAbstractLoop):
    @staticmethod
    def create_event_loop():
        return LibevLoop()
