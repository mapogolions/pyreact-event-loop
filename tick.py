import queue


class FutureTickQueue:
    def __init__(self, size=0):
        self.queue = queue.Queue(size)

    def empty(self):
        return self.queue.empty()

    def add(self, listener):
        self.queue.put(listener)

    def tick(self):
        while not self.queue.empty():
            listener = self.queue.get()
            listener()


if __name__ == "__main__":
    q = FutureTickQueue()
    assert q.empty() is True, "Queue is empty"
    side_effect = []
    q.add(lambda: side_effect.append("first"))
    q.add(lambda: side_effect.append("second"))
    assert q.empty() is False, "Queue isn't empty"
    q.tick()
    assert side_effect[0] == "first", ""
    assert side_effect[1] == "second", ""
    assert q.empty() is True, "Queue again is empty"
