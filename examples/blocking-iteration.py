import event_loop


def foreach(f, source):
    for item in source:
        f(item)


loop = event_loop.SelectLoop()
loop.add_timer(0, lambda: print("timeout 0"))
loop.future_tick(lambda: foreach(print, range(10**2)))  # blocking
loop.run()