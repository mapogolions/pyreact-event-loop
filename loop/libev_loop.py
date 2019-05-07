from mood.event import EvLoop

from loop.tick import FutureTickQueue
from loop.signal import Signals


class LibevLoop:
    def __init__(self):
        self.loop = EvLoop()
        self.future_tick_queue = FutureTickQueue()
        self.timers = None # SplObjectStorage
        self.read_streams = None # EvIo[]
        self.write_streams = None # EvIo[]
        self.running = False
        self.signals = Signals()
        self.signal_events = None # EvSignal[]
