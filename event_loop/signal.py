class Signals:
    def __init__(self):
        self.signals = {}

    def empty(self):
        return len(self.signals) == 0

    def count(self, signum):
        if signum not in self.signals:
            return 0
        return len(self.signals[signum])

    def call(self, signum):
        if signum in self.signals:
            for listener in self.signals[signum]:
                listener()

    def add(self, signum, listener):
        if signum not in self.signals:
            self.signals[signum] = []
        if listener not in self.signals[signum]:
            self.signals[signum].append(listener)

    def remove(self, signum, listener):
        if signum not in self.signals:
            return
        if listener not in self.signals[signum]:
            return
        self.signals[signum].remove(listener)
        if not self.signals[signum]:
            del self.signals[signum]
