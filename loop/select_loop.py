import signal

from loop.tick import FutureTickQueue
from loop.timer import Timer, Timers
from loop.signal import Signals


MICROSECONDS_PER_SECOND = 10 ** 6


class SelectLoop:
    def __init__(self):
        self.future_tick_queue = FutureTickQueue()
        self.timers = Timers()
        self.read_streams = {}
        self.read_listeners = {}
        self.write_streams = {}
        self.write_listeners = {}
        self.running = False
        self.signals = Signals()

    def add_read_stream(self, stream, listener):
        key = int(stream)
        if key not in self.read_streams:
            self.read_streams[key] = stream
            self.read_listeners[key] = listener

    def add_write_stream(self, stream, listener):
        key = int(stream)
        if key not in self.write_streams:
            self.write_streams[key] = stream
            self.write_listeners[key] = listener

    def remove_read_stream(self, stream):
        key = int(stream)
        if key in self.read_streams:
            del self.read_streams[key]
            del self.read_listeners[key]

    def remove_write_stream(self, stream):
        key = int(stream)
        if key in self.write_streams:
            del self.write_streams[key]
            del self.write_listeners[key]

    def add_timer(self, interval, callback):
        timer = Timer(interval, callback, periodic=False)
        self.timers.add(timer)
        return timer

    def add_periodic_timer(self, interval, callback):
        timer = Timer(interval, callback, periodic=True)
        self.timers.add(timer)
        return timer

    def cancel_timer(self, timer):
        return self.timers.cancel(timer)

    def future_tick(self, listener):
        self.future_tick_queue.add(listener)

    def add_signal(self, signum, listener):
        first = self.signals.count(signum)
        self.signals.add(signum, listener)
        if first:
            signal.signal(signum, lambda *meta: self.signals.call(meta[0]))

    def remove_signal(self, signum, listener):
        if self.signals.count(signum) == 0:
            return
        self.signals.remove(signum, listener)
        if self.signals.count(signum) == 0:
            signal.signal(signum, signal.SIG_DFL)

    def stop(self):
        self.running = False
