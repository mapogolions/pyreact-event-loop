import time
import heapq


MIN_INTERVAL = 0.000001


class Timer:
    def __init__(self, interval, callback, periodic=False):
        self.interval = MIN_INTERVAL if interval < MIN_INTERVAL else interval
        self.callback = callback
        self.periodic = periodic


class Timers:
    def __init__(self):
        self.time = None
        self.timers = {}
        self.schedule = []

    def tick(self):
        timestamp = self.update_time()
        while self.schedule and self.schedule[0][0] < timestamp:
            _, tid, timer = heapq.heappop(self.schedule)
            if tid not in self.timers or timer is not self.timers[tid]:
                continue
            timer = self.timers[tid]
            timer.callback()
            if timer.periodic:
                heapq.heappush(
                    self.schedule,
                    (timestamp + timer.interval, tid, timer)
                )
            else:
                self.garbage_collect(tid)

    def __contains__(self, timer):
        return hash(timer) in self.timers

    def get_time(self):
        return self.update_time() if self.time is None else self.time

    def update_time(self):
        self.time = time.time()
        return self.time

    def empty(self):
        return len(self.timers) == 0

    def add(self, timer):
        tid = hash(timer)
        self.timers[tid] = timer
        heapq.heappush(
            self.schedule,
            (timer.interval + self.update_time(), tid, timer)
        )

    def cancel(self, timer):
        return self.garbage_collect(hash(timer))

    def get_first(self):
        if not self.schedule:
            return None
        scheduled_at, tid, _ = self.schedule[0]
        return (scheduled_at, self.timers[tid])

    def garbage_collect(self, tid):
        if tid not in self.timers:
            return False
        del self.timers[tid]
        for i in range(0, len(self.schedule)):
            _, key, _ = self.schedule[i]
            if tid == key:
                self.schedule.pop(i)
                heapq.heapify(self.schedule)
        return True
