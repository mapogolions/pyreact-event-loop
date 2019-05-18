```python
import socket
import event_loop


def process_incoming_connection(stream):
    conn, addr = stream.accept()
    print("Incoming connection from ", addr)
    loop.add_read_stream(conn, read)


def read(stream):
    data = stream.recv(2**16)
    if not data or data.startswith(b'quit'):
        stream.close()
        loop.remove_read_stream(stream)
    else:
        loop.add_write_stream(stream, echo(data))


def echo(data):
    def f(stream):
        stream.send(data)
        loop.remove_write_stream(stream)
    return f


HOST, PORT = ("localhost", 8080)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.bind((HOST, PORT))
server.listen(5)

loop = event_loop.SelectLoop()
loop.add_read_stream(server, process_incoming_connection)
loop.add_periodic_timer(5, lambda: print("tick"))

print("[SERVER] host: %s, port: %d" % (HOST, PORT))
loop.run()
```
