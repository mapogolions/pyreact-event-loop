## Pyreact event loop

[![Build Status](https://travis-ci.org/mapogolions/pyreact-event-loop.svg?branch=master)](https://travis-ci.org/mapogolions/pyreact-event-loop) [![Coverage Status](https://coveralls.io/repos/github/mapogolions/pyreact-event-loop/badge.svg?branch=master)](https://coveralls.io/github/mapogolions/pyreact-event-loop?branch=master) [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](./LICENSE.txt)

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
loop.future_tick(lambda: print("Hello "))
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
docker build github.com/mapogolions/pyreact-event-loop -t mapogolions/eventloop
docker run -it mapogolions/eventloop # ./timers.py
# or you could pass a relative file path
docker run -it mapogolions/eventloop ./periodic.py
docker run -it mapogolions/eventloop ./fp-streams.py
```

__[For deployment see .travis.yml](./.travis.yml)__
