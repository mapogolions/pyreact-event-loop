import event_loop


loop = event_loop.SelectLoop()
timer = loop.add_periodic_timer(1, lambda: print("tick-tack"))
loop.add_timer(4.1, lambda: loop.cancel_timer(timer))
loop.run()
