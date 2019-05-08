import mood.event as libev

from loop.tick import FutureTickQueue
from loop.signal import Signals
from loop.timer import Timer


class LibevLoop:
    def __init__(self):
        self.loop = libev.Loop()
        self.future_tick_queue = FutureTickQueue()
        self.timers = {}
        self.read_streams = {}
        self.write_streams = {}
        self.running = False
        self.signals = Signals()
        self.signal_events = {}

    def add_read_stream(self, stream, listener):
        key = hash(stream)
        if key not in self.read_streams:
            ev_io = self.loop.io(
                stream,
                libev.EV_READ,
                lambda *args: listener(stream)
            )
            ev_io.start()
            self.read_streams[key] = ev_io

    def add_write_stream(self, stream, listener):
        key = hash(stream)
        if key not in self.write_streams:
            ev_io = self.loop.io(
                stream,
                libev.EV_WRITE,
                lambda *args: listener(stream)
            )
            ev_io.start()
            self.write_streams[key] = ev_io

    def remove_read_stream(self, stream):
        key = hash(stream)
        if key in self.read_streams:
            self.read_streams[key].stop()
            del self.read_streams[key]

    def remove_write_stream(self, stream):
        key = hash(stream)
        if key in self.write_streams:
            self.write_streams[key].stop()
            del self.write_streams[key]

    def add_timer(self, interval, callback):
        timer = Timer(interval, callback)
        key = hash(timer)

        def action(*args):
            nonlocal timer
            timer.callback()
            self.cancel_timer(timer)
        ev_timer = self.loop.timer(timer.interval, 0.0, action)
        ev_timer.start()
        self.timers[key] = ev_timer
        return timer

    def add_periodic_timer(self, interval, callback):
        timer = Timer(interval, callback)
        key = hash(timer)
        ev_timer = self.loop.timer(
            timer.interval,
            timer.interval,
            timer.callback
        )
        ev_timer.start()
        self.timers[key] = ev_timer
        return timer

    def cancel_timer(self, timer):
        key = hash(timer)
        if key in self.timers:
            self.timers[key].stop()
            del self.timers[key]

    def future_tick(self, listener):
        self.future_tick_queue.add(listener)

    def stop(self):
        self.running = False

    def add_signal(self, signum, listener):
        self.signals.add(signum, listener)
        if signum not in self.signal_events:
            ev_signal = self.loop.signal(
                signum,
                lambda *args: self.signals.call(signum)
            )
            ev_signal.start()
            self.signal_events[signum] = ev_signal

    def remove_signal(self, signum, listener):
        self.signals.remove(signum, listener)
        if not self.signals.count(signum):
            self.signal_events[signum].stop()
            del self.signal_events[signum]

    def run(self):
        self.running = True
        while self.running:
            self.future_tick_queue.tick()
            has_pending_callbacks = not self.future_tick_queue.empty()
            was_just_stopped = not self.running
            nothing_left_to_do = (not self.read_streams and
                                  not self.write_streams and
                                  not self.timers and
                                  self.signals.empty())

            if was_just_stopped or has_pending_callbacks:
                self.loop.start(libev.EVRUN_NOWAIT)
            elif nothing_left_to_do:
                break
            else:
                self.loop.start(libev.EVRUN_ONCE)
