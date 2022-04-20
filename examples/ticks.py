import event_loop


loop = event_loop.SelectLoop()
loop.future_tick(lambda: print("b"))
loop.future_tick(lambda: print("c"))
print("a")
loop.run()
