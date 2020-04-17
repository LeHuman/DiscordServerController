import socket
import ssl

hostname = "99.127.217.73"
context = ssl.create_default_context()

with socket.create_connection((hostname, 4578)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.version())
