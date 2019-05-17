```python
import os
import signal

import event_loop


def handle_signal():
    print("Success")
    loop.remove_signal(signal.SIGINT, handle_signal)


loop = event_loop.SelectLoop()
loop.add_signal(signal.SIGINT, handle_signal)
print("Listening of SIGINT. Use kill -SIGINT %d or CTRL-C" % os.getpid())
loop.run()
```
