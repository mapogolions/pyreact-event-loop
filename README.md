## Pyreact event loop


Event loop uses a single thread and is responsible for scheduling asynchronous operations. Module `event_loop` provides several implementation of the event loop.

There are three available implementations:

* `SelectLoop` uses the [`select`](https://docs.python.org/3/library/select.html) module
* `LibevLoop` uses the [`mood.event`](https://github.com/lekma/mood.event) python `libev` interface
* `LibuvLoop` uses the [`pyuv`](https://github.com/saghul/pyuv) python interface for `libuv`


### How to use

```sh
(env) $ git clone <url>
(env) $ cd project
(env) $ pip install -r requirements.txt
(env) $ pytest
(env) $ python setup.py install
(env) $ python
>>> import event_loop
>>> loop = event_loop.SelectLoop()
>>> loop.add_periodic_timer(2, lambda: print('tick'))
>>> loop.run()
```
