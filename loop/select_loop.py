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

    def helper(self, signum):
        signal.call

    def add_signal(self, signum, listener):
        self.signals.add(signum, listener)
        if self.signals.count(signum) == 1:
            signal.signal(
                signum,
                lambda *args: self.signals.call(args[0])
            )

    def remove_signal(self, signum, listener):
        if not self.signals.count(signum):
            return
        self.signals.remove(signum, listener)
        if not self.signals.count(signum):
            signal.signal(signum, signal.SIG_DFL)

    def stop(self):
        self.running = False

    # not complete !!!
    def launch(self):
        self.running = True
        while self.running:
            self.future_tick_queue.tick()
            self.timers.tick()
            struct_timer_info = self.timers.get_first()

            """event_loop.future_tick( lambda: event_loop.future_tick(lambda: pass) )"""
            """event_loop.add_timer(0.03, lambda: event_loop.future_tick(lambda: pass))"""
            """event_loop.future_tick( lambda: event_loop.stop() ) """
            if not self.running or not self.future_tick_queue.empty():
                pass
            elif struct_timer_info:
                self.wait_for_timers_execution(struct_timer_info)
            elif self.read_streams or self.write_streams:
                self.notify(self.select_stream(None))
            elif not self.signals.empty():
                signal.pause()
            else:
                break

    def wait_for_timers_execution(self, struct_timer_info):
        (scheduled_at, timer) = struct_timer_info
        timeout = self.define_timeout(scheduled_at - self.timers.get_time())
        if self.read_streams or self.write_streams:
            self.notify(self.select_stream(timeout))
        else:
            time.sleep(timeout)


    def define_timeout(self, timeout):
        if timeout < 0:
            return 0
        timeout /= MICROSECONDS_PER_SECOND
        return sys.maxsize if timeout > sys.maxsize else timeout

    def stream_select(self, timeout):
        (rs, ws) = (self.read_streams, self.write_streams)
        return select.select(rs, ws, [], timeout)

    def nofity(self, streams):
        if streams:
            return
        (rs, ws, _) = streams
        for stream in rs:
            listener = self.read_listeners[int(stream)]
            listener(stream)
        for stream in ws:
            listener = self.write_streams[int(stream)]
            listener(stream)
