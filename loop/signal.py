class Signals:
    def __init__(self):
        self.signals = {}

    def empty(self):
        return len(self.signals) == 0

    def count(self, signal):
        if signal not in self.signals:
            return 0
        return len(self.signals[signal])

    def call(self, signal):
        if signal in self.signals:
            for listener in self.signals[signal]:
                listener()

    def add(self, signal, listener):
        if signal not in  self.signals:
            self.signals[signal] = []
        if listener not in self.signals[signal]:
            self.signals[signal].append(listener)

    def remove(self, signal, listener):
        if signal not in self.signals:
            return False
        if listener not in self.signals[signal]:
            return False
        self.signals[signal].remove(listener)
        if not self.signals[signal]:
            del self.signals[signal]
        return True
