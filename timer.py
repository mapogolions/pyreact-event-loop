import time
from collections import OrderedDict


MIN_INTERVAL = 0.000001


class Timer:
    def __init__(self, interval, callback, periodic=False):
        self.interval = MIN_INTERVAL if interval < MIN_INTERVAL else interval
        self.callback = callback
        self.periodic = periodic


class Timers:
    def __init__(self):
        self._time = None
        self.timers = {}
        self.schedule = OrderedDict()
        self.sorted = False

    def tick():
        if not self.sorted:
            self.sort_by_time()
        time = self.time
        for (id, scheduled_in) in self.schedule.items():
            if scheduled_in >= time:
                return
            timer = self.timers[id]
            timer.callback()
            del self.timers[id]
            del self.schedule[id]

    def sort_by_time(self):
        self.sorted = True
        self.schedule = OrderedDict(
            sorted(self.schedule.items(), lambda xs: xs[1])
        )

    def __contains__(self, timer):
        return hash(timer) in self.timers

    @property
    def time(self):
        return self.update_time() if self._time is None else self._time

    def update_time(self):
        self._time = time.time()
        return self._time

    def empty(self):
        return len(self.timers) == 0

    def add(self, timer):
        id = hash(timer)
        self.timers[id] = timer
        self.schedule[id] = timer.interval + self.update_time()
        self.sorted = False

    def cancel(self, timer):
        id = hash(timer)
        del self.timers[id]
        del self.schedule[id]

    def get_first(self):
        if not self.sorted:
            self.sorted = True
            self.schedule = OrderedDict(
                sorted(self.schedule.items(), lambda xs: xs[1])
            )
        return self.schedule.items(0)
