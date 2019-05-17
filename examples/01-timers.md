```python
import event_loop


loop = event_loop.SelectLoop()
loop.add_timer(1, lambda: print("world!"))
loop.add_timer(0.5, lambda: print("hello "))
loop.run()
```
