### Iteration

#### Blocking
```python
import event_loop


def foreach(f, source):
    for item in source:
        f(item)


loop = event_loop.SelectLoop()
loop.add_timer(0, lambda: print("timeout 0"))
loop.future_tick(lambda: foreach(print, range(10**3)))  # blocking operation
loop.run()
```

#### Non-blocking

```python
import event_loop


def foreach(fn, source):
    def do(index):
        if index >= len(source):
            loop.cancel_timer(timer)
            print("done")
            return
        def forward():
            fn(index, source[index])
            do(index + 1)
        loop.add_timer(0, forward)
    return do(0)


numbers = list(range(10**2))
loop = event_loop.LibuvLoop()
loop.add_timer(0, lambda: print("timeout 0"))
timer = loop.add_periodic_timer(0.005, lambda: print("-" * 10))
loop.future_tick(lambda: foreach(print, range(10**3)))  # non-blocking operation
loop.run()
```
