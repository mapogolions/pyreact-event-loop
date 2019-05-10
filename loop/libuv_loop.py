import pyuv as libuv

from loop.tick import FutureTickQueue
from loop.signal import Signals
from loop.timer import Timer


SUB_MS_ACCURACY = 10e-4


class LibuvLoop:
    def __init__(self):
        self.uv_loop = libuv.Loop()
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
            uv_poll = libuv.Poll(self.uv_loop, stream.fileno())
            uv_poll.start(libuv.UV_READABLE, lambda *args: listener(stream))
            self.read_streams[key] = uv_poll

    def add_write_stream(self, stream, listener):
        key = hash(stream)
        if key not in self.write_streams:
            uv_poll = libuv.Poll(self.uv_loop, stream.fileno())
            uv_poll.start(libuv.UV_WRITABLE, lambda *args: listener(stream))
            self.write_streams[key] = uv_poll

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
        timer = Timer(
            interval if interval > SUB_MS_ACCURACY else SUB_MS_ACCURACY,
            callback,
            periodic=False
        )

        def action(*args):
            nonlocal timer
            timer.callback()
            self.cancel_timer(timer)

        uv_timer = libuv.Timer(self.uv_loop)
        uv_timer.start(action, timer.interval, 0.0)
        self.timers[hash(timer)] = uv_timer
        return timer

    def add_periodic_timer(self, interval, callback):
        timer = Timer(
            interval if interval > SUB_MS_ACCURACY else SUB_MS_ACCURACY,
            callback,
            periodic=True
        )
        uv_timer = libuv.Timer(self.uv_loop)
        uv_timer.start(timer.callback, timer.interval, timer.interval)
        self.timers[hash(timer)] = uv_timer
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
            uv_signal = libuv.Signal(self.uv_loop)
            uv_signal.start(
                lambda *args: self.signals.call(signum),
                signum
            )
            self.signal_events[signum] = uv_signal

    def remove_signal(self, signum, listener):
        if signum not in self.signal_events:
            return
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
                self.uv_loop.run(libuv.UV_RUN_NOWAIT)
            elif nothing_left_to_do:
                break
            else:
                self.uv_loop.run(libuv.UV_RUN_ONCE)
