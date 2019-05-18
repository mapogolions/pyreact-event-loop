```python
import socket
import event_loop


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.bind(('localhost', 8080))
server.listen(5)


def handle_incoming_connection(rstream):
    conn, addr = rstream.accept()
    data = b"HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nHi\n"

    def send(wstream):
        nonlocal data
        written = wstream.send(data)
        if written == len(data):
            loop.remove_write_stream(wstream)
            wstream.close()
        else:
            data = data[written:]

    loop.add_write_stream(conn, send)

loop = event_loop.SelectLoop()
loop.add_read_stream(server, handle_incoming_connection)
loop.add_periodic_timer(2, lambda: print("tick"))
loop.run()
```
