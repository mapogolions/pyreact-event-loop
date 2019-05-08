import unittest

from loop.select_loop import SelectLoop
from tests.test_abstract_loop import TestAbstractLoop


class TestSelectLoop(unittest.TestCase, TestAbstractLoop):
    @staticmethod
    def create_event_loop():
        return SelectLoop()
