import event_loop


def foreach(fn, source):
    def forward(source, index):
        def f():
            fn(source[index])
            do(index + 1)
        return f

    def do(index):
        if index < len(source):
            loop.add_timer(0, forward(source, index))

    return do(0)


loop = event_loop.LibuvLoop()
loop.add_timer(0, lambda: print("timeout 0"))
loop.future_tick(lambda: foreach(print, range(10**2))) 
loop.run()
