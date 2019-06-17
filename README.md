## Pyreact event loop

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/mapogolions/pyreact-event-loop) [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](./LICENSE.txt)

It's modest attempt to implement the reactor pattern to break the traditional synchronous flow. The event loop uses a single thread and is responsible for scheduling asynchronous operations.


### Introduction

In JS event loop is available out of the box. It is working behind the scenes. Asynchronous code in JS looks like this:

```js
setTimeout(() => console.log('world!'), 1000);
console.log("Hello ");
```

the same things with `pyreact-event-loop`:

```python
loop = event_loop.SelectLoop()
loop.add_timer(1, lambda: print("world!"))
print("Hello ")
loop.run()
```

In python needs to explicitly define the event loop.


### By standing on the shoulders of [Giants](https://reactphp.org/event-loop/)

`Pyreact-event-loop` based on [`ReactPHP event loop`](https://reactphp.org/event-loop/) component.

There are three available implementations:

* `SelectLoop` uses the [`select`](https://docs.python.org/3/library/select.html) module
* `LibevLoop` uses the [`mood.event`](https://github.com/lekma/mood.event) python `libev` interface
* `LibuvLoop` uses the [`pyuv`](https://github.com/saghul/pyuv) python interface for `libuv`


### Examples

* [timers](./examples/01-timers.md)
* [periodic timers](./examples/02-periodic.md)
* [ticks](./examples/03-ticks.md)
* [signals](./examples/04-signals.md)
* [echo server](./examples/05-echo-server.md)
* [fp streams](./examples/06-fp-streams.md)
* [non-blocking iteration](./examples/07-non-blocking-iteration.md)


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
