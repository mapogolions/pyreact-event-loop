```python
import event_loop


def noop():
    pass


def empty_stream(cb):
    return noop


def of(x):
    def func(cb):
        cb(x)
        return noop
    return func


def prepend(x, stream):
    def func(cb):
        cb(x)
        return stream(cb)
    return func


def later(delay):
    def func(f):
        timer = loop.add_timer(delay, f)
        return lambda: loop.cancel_timer(timer)
    return func


def of_many(delay, seq):
    def func(cb):
        it, stream, unsubcribe = iter(seq), later(delay), noop
        def doit():
            nonlocal unsubcribe
            try:
                current = next(it)
                unsubcribe = stream(lambda: doit())
                cb(current)
            except StopIteration:
                pass
        unsubcribe = stream(lambda: doit())
        return lambda: unsubcribe()
    return func


def map_stream(f, stream):
    def func(cb):
        return stream(lambda x: cb(f(x)))
    return func


def filter_stream(f, stream):
    def func(cb):
        def predicate(x):
            if f(x):
                cb(x)
        return stream(predicate)
    return func


def infinite_seq():
    counter = 0
    while True:
        yield counter
        counter += 1


loop = event_loop.SelectLoop()
sequence = of_many(0.5, infinite_seq())
even_nums = filter_stream(lambda x: x % 2 == 0, sequence)
unsubscribe = map_stream(lambda x: [x, x ** 2], even_nums)(print)
loop.add_timer(8.1, unsubscribe)
loop.run()
```
