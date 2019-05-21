import queue


class FutureTickQueue:
    def __init__(self, size=0):
        self.queue = queue.Queue(size)

    def empty(self):
        return self.queue.empty()

    def add(self, listener):
        self.queue.put(listener)

    def tick(self):
        amount = self.queue.qsize()
        while amount > 0:
            amount -= 1
            listener = self.queue.get()
            listener()
