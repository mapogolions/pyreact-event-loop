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
        return True


if __name__ == "__main__":
    signals = Signals()
    assert signals.empty() is True, "Empty"
    assert signals.remove("JUCE_SIGNAL", lambda: None) is False, ""
    assert signals.count("JUCE_SIGNAL") == 0, ""
    side_effect = []
    juce_signal_first = lambda: side_effect.append("JUCE_SIGNAL_FIRST")
    juce_signal_second = lambda: side_effect.append("JUCE_SIGNAL_SECOND")
    signals.add("JUCE_SIGNAL", juce_signal_first)
    assert signals.count("JUCE_SIGNAL") == 1, ""
    assert signals.empty() is False, ""
    signals.add("JUCE_SIGNAL", juce_signal_second)
    assert signals.count("JUCE_SIGNAL") == 2, ""
    assert signals.remove("JUCE_SIGNAL", juce_signal_first) is True, ""
    assert signals.count("JUCE_SIGNAL") == 1, ""
    signals.call("JUCE_SIGNAL")
    assert side_effect[0] == "JUCE_SIGNAL_SECOND", ""
