import event_loop


loop = event_loop.SelectLoop()
loop.add_timer(3, lambda: print("world!"))
loop.add_timer(1.5, lambda: print("hello "))
loop.run()
