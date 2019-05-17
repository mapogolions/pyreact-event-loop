import select
import signal
import time

import event_loop.tick
import event_loop.timer
import event_loop.signal


MICROSECONDS_PER_SECOND = 10 ** 6
MAX_TIMEOUT = int(2 ** 63 / 10 ** 9)


class SelectLoop:
    def __init__(self):
        self.future_tick_queue = event_loop.tick.FutureTickQueue()
        self.timers = event_loop.timer.Timers()
        self.read_streams = []
        self.read_listeners = {}
        self.write_streams = []
        self.write_listeners = {}
        self.running = False
        self.signals = event_loop.signal.Signals()
        self.pcntl_signals = []

    def add_read_stream(self, stream, listener):
        if stream.fileno() == -1:
            raise ValueError
        key = hash(stream)
        if key not in self.read_listeners:
            self.read_streams.append(stream)
            self.read_listeners[key] = listener

    def add_write_stream(self, stream, listener):
        if stream.fileno() == -1:
            raise ValueError
        key = hash(stream)
        if key not in self.write_listeners:
            self.write_streams.append(stream)
            self.write_listeners[key] = listener

    def remove_read_stream(self, stream):
        key = hash(stream)
        if key in self.read_listeners:
            self.read_streams.remove(stream)
            del self.read_listeners[key]

    def remove_write_stream(self, stream):
        key = hash(stream)
        if key in self.write_listeners:
            self.write_streams.remove(stream)
            del self.write_listeners[key]

    def add_timer(self, interval, callback):
        timer = event_loop.timer.Timer(interval, callback, periodic=False)
        self.timers.add(timer)
        return timer

    def add_periodic_timer(self, interval, callback):
        timer = event_loop.timer.Timer(interval, callback, periodic=True)
        self.timers.add(timer)
        return timer

    def cancel_timer(self, timer):
        return self.timers.cancel(timer)

    def future_tick(self, listener):
        self.future_tick_queue.add(listener)

    def pcntl_signal_dispatch(self):
        for signum in self.pcntl_signals:
            self.signals.call(signum)
        self.pcntl_signals = []

    def add_signal(self, signum, listener):
        self.signals.add(signum, listener)
        if self.signals.count(signum) == 1:
            signal.signal(
                signum,
                lambda *args: self.pcntl_signals.append(signum)
            )

    def remove_signal(self, signum, listener):
        if not self.signals.count(signum):
            return
        self.signals.remove(signum, listener)
        if not self.signals.count(signum):
            signal.signal(signum, signal.SIG_DFL)

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.future_tick_queue.tick()
            self.timers.tick()
            self.pcntl_signal_dispatch()

            has_pending_callbacks = not self.future_tick_queue.empty()
            was_just_stopped = not self.running
            has_pending_timer = self.timers.get_first()
            has_pending_io = self.read_streams or self.write_streams
            has_pending_signals = not self.signals.empty()

            if was_just_stopped or has_pending_callbacks:
                self.notify(self.select_stream(timeout=0))
            elif has_pending_timer:
                self.wait_for_timers(has_pending_timer)
            elif has_pending_io:
                self.notify(self.select_stream(timeout=None))
            elif has_pending_signals:
                signal.pause()
            else:
                break

    def wait_for_timers(self, pending_timer):
        scheduled_at, _ = pending_timer
        timeout = self.time_to_sleep(scheduled_at - self.timers.get_time())
        if self.read_streams or self.write_streams:
            self.notify(self.select_stream(timeout=timeout))
        else:
            time.sleep(timeout)

    def time_to_sleep(self, timeout):
        if timeout < 0:
            return 0
        timeout /= MICROSECONDS_PER_SECOND
        return MAX_TIMEOUT if timeout > MAX_TIMEOUT else timeout

    def select_stream(self, timeout):
        return select.select(
            self.read_streams,
            self.write_streams,
            [],
            timeout
        )

    def notify(self, streams):
        if not streams:
            return
        ready_to_read, ready_to_write, _ = streams
        for stream in ready_to_read:
            listener = self.read_listeners[hash(stream)]
            listener(stream)
        for stream in ready_to_write:
            listener = self.write_listeners[hash(stream)]
            listener(stream)
