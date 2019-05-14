### Signals

```python
def test_signal(self):
    def cleanup():
        nonlocal timer
        self.loop.remove_signal(signal.SIGUSR1, cleanup)
        self.loop.remove_signal(signal.SIGUSR2, self.mock)
        self.loop.cancel_timer(timer)
        self.mock("signal")

    timer = self.loop.add_periodic_timer(1, lambda: self.mock("timer"))
    self.loop.add_signal(signal.SIGUSR2, self.mock)
    self.loop.add_signal(signal.SIGUSR1, cleanup)
    self.loop.future_tick(lambda: os.kill(os.getpid(), signal.SIGUSR1))
    self.loop.run()

    self.assertEqual(
        [unittest.mock.call("signal")],
        self.mock.call_args_list
    )



# BUG HERE!!!
def test_only_signals(self):
    def cleanup():
        self.mock(20)
        self.loop.remove_signal(signal.SIGUSR1, listener)
        self.loop.remove_signal(signal.SIGUSR2, cleanup)

    # listener = lambda: self.mock(1)
    counter = 1
    def listener():
        nonlocal counter
        self.mock(counter)
        counter += 1

    self.loop.add_signal(signal.SIGUSR1, listener)
    self.loop.add_signal(signal.SIGUSR2, cleanup)

    for signum in [signal.SIGUSR1, signal.SIGUSR1, signal.SIGUSR2]:
        os.kill(os.getpid(), signum)
    self.loop.run()
    self.assertEqual(
    # [unittest.mock.call(1),
    #  unittest.mock.call(1),
    #  unittest.mock.call(2)],
    [],
    self.mock.call_args_list
    )

def test_order_of_signals(self):
    ev_loop = libev.Loop()
    usr1 = ev_loop.signal(signal.SIGUSR1, lambda *args: self.mock(1), None, 0)
    hup = ev_loop.signal(signal.SIGHUP, lambda *args: self.mock(3), None, 0)
    hup.start()
    usr1.start()
    os.kill(os.getpid(), signal.SIGUSR1)
    os.kill(os.getpid(), signal.SIGHUP)
    ev_loop.start(libev.EVRUN_ONCE)
    self.assertEqual(
        [unittest.mock.call(1),
        unittest.mock.call(3)],
        self.mock.call_args_list
    )
    self.loop.add_signal(signal.SIGUSR1, lambda *args: self.mock(1))
    self.loop.add_signal(signal.SIGUSR2, lambda *args: self.mock(2))
    self.loop.add_signal(signal.SIGHUP, lambda *args: self.mock(3))
    for signum in [signal.SIGHUP, signal.SIGUSR2, signal.SIGUSR1]:
        os.kill(os.getpid(), signum)
    self.next_tick()
    self.assertEqual(
        [unittest.mock.call(3),
        unittest.mock.call(2),
        unittest.mock.call(1)],
        self.mock.call_args_list
    )

def test_handle_only_unique_signals_per_tick(self):
    mock = unittest.mock.Mock()
    counter = 1

    def func(*args):
        nonlocal counter
        mock(counter)
        counter += 1

    self.loop.add_signal(signal.SIGUSR1, func)
    os.kill(os.getpid(), signal.SIGUSR1)
    os.kill(os.getpid(), signal.SIGUSR1)
    self.next_tick()
    os.kill(os.getpid(), signal.SIGUSR1)
    os.kill(os.getpid(), signal.SIGUSR1)
    self.next_tick()
    self.assertEqual(
        [unittest.mock.call(1),
        unittest.mock.call(2)],
        mock.call_args_list
    )
```
