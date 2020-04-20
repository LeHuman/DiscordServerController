import socket
import ssl

hostname = "www.koolkidz.club"
context = ssl.SSLContext(ssl.PROTOCOL_TLS)

with socket.create_connection((hostname, 4578)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.version())
        ssock.close()
