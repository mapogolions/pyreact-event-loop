import select
import sys
import signal
import time

from loop.tick import FutureTickQueue
from loop.timer import Timer, Timers
from loop.signal import Signals


MICROSECONDS_PER_SECOND = 10 ** 6


class SelectLoop:
    def __init__(self):
        self.future_tick_queue = FutureTickQueue()
        self.timers = Timers()
        self.read_streams = []
        self.read_listeners = {}
        self.write_streams = []
        self.write_listeners = {}
        self.running = False
        self.signals = Signals()

    def add_read_stream(self, stream, listener):
        if stream not in self.read_streams:
            self.read_streams.append(stream)
            self.read_listeners[int(stream)] = listener

    def add_write_stream(self, stream, listener):
        if stream not in self.write_streams:
            self.write_streams.append(stream)
            self.write_listeners[int(stream)] = listener

    def remove_read_stream(self, stream):
        if stream in self.read_streams:
            self.read_streams.remove(stream)
            del self.read_listeners[int(stream)]

    def remove_write_stream(self, stream):
        if stream in self.write_streams:
            self.write_streams.remove(stream)
            del self.write_listeners[int(stream)]

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

    # not complete !!!
    def run(self):
        self.running = True
        while self.running:
            self.future_tick_queue.tick()
            self.timers.tick()
            metadata = self.timers.get_first()
            if metadata:
                timeout = None
                if self.stream_select(timeout):
                    self.nofity()
            elif self.read_streams or self.write_streams:
                if self.stream_select(None):
                    self.notify()
            elif not self.signals.empty():
                self.wait_for_come_signals()
            else:
                break

    def stream_select(self, timeout):
        return select.select(
            self.read_streams,
            self.write_streams,
            [],
            timeout
        )

    def wait_for_come_signals(self):
        time.sleep(sys.maxsize)

    def nofity(self):
        for stream in self.read_streams:
            listener = self.read_listeners[int(stream)]
            listener(stream)
        for stream in self.write_streams:
            listener = self.write_streams[int(stream)]
            listener(stream)
