import socket
import ssl

# context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain("cert.pem", "key.pem")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(("192.168.1.217", 4578))
    sock.listen(5)
    with context.wrap_socket(sock, server_side=True) as ssock:
        conn, addr = ssock.accept()
