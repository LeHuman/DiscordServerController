import socket
import ssl
import time
from datetime import datetime
from enum import Enum
from threading import Thread

HOST = "192.168.1.217"
PORT = 4578
CERT = "cert.pem"
KEY = "key.pem"
TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/" + TARGET_SERVER
print("HOST: ", HOST)
print("PORT: ", PORT)
print("TARGET SERVER: ", TARGET_SERVER)


# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock = socket.socket()
# sock.bind((HOST, PORT))
# sock.listen(5)
# context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# context.load_cert_chain(keyfile=KEY, certfile=CERT)  # 1. key, 2. cert, 3. intermediates
# context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # optional
# context.set_ciphers("EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH")


class Status(Enum):
    ON = 10
    TURNING_ON = 5
    TURNING_OFF = 2
    OFF = 0


statusString = {
    Status.ON: "ON",
    Status.TURNING_ON: "TURNING ON",
    Status.TURNING_OFF: "TURNING OFF",
    Status.OFF: "OFF",
}


SERVERSTATUS = Status.OFF


class Command(Enum):
    triggerOn = 15
    triggerOff = 12  # is this a good idea?
    check = 8


def SERVERON():
    SERVERSTATUS == Status.TURNING_ON
    return


def SERVEROFF():
    SERVERSTATUS == Status.TURNING_OFF
    return


def order(cmd):

    print("Recieved command:", cmd)

    if cmd == Command.check.value:
        return statusString[SERVERSTATUS]

    if SERVERSTATUS == Status.ON:
        if cmd == Command.triggerOn.value:
            return "Server already on!"
        elif cmd == Command.triggerOff.value:
            SERVEROFF()
            return "Turning off server!"
    elif SERVERSTATUS == Status.OFF:
        if cmd == Command.triggerOn.value:
            SERVERON()
            return "Turning on server!"
        elif cmd == Command.triggerOff.value:
            return "Server already off!"
    elif cmd == Command.triggerOn.value or Command.triggerOn.value:
        if SERVERSTATUS == Status.TURNING_OFF:
            return "Server is Turning off!"
        elif SERVERSTATUS == Status.TURNING_ON:
            return "Server is Turning on!"

    return "Unknown command"


class client(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        print("New Client:", address)
        self.start()

    def msg(self, message):
        self.sock.send(message.encode())
        print(message)

    def end(self):
        self.sock.close()

    def run(self):
        recieve = self.sock.recv(256).decode()
        try:
            recieve = int(recieve)
        except:
            self.msg("Bad Command")
            print("command:", recieve)
            self.end()
            return

        self.msg(order(recieve))
        self.end()


def handle(conn):
    print(conn.recv(256).decode())
    conn.write(b"HTTP/1.1 200 OK\n\n%s" % conn.getpeername()[0].encode())


# def socketLoop():
#     wrappedSocket.listen(2)
#     print("Command server started")
#     while not (SERVERSTATUS == Status.TURNING_OFF or SERVERSTATUS == Status.TURNING_ON):
#         clientsocket, address = wrappedSocket.accept()
#         client(clientsocket, address)


# while not (SERVERSTATUS == Status.TURNING_OFF or SERVERSTATUS == Status.TURNING_ON):
#     conn = None
#     ssock, addr = sock.accept()
#     try:
#         conn = context.wrap_socket(ssock, server_side=True)
#         handle(conn)
#     except ssl.SSLError as e:
#         print(e)
#     finally:
#         if conn:
#             conn.close()

# while 1:
#     socketLoop()
#     # TODO: how are we actually turning the server on?


def deal_with_client(connstream):
    data = connstream.recv(1024)
    # empty data means the client is finished with us
    while data:
        # if not do_something(connstream, data):
            # we'll assume do_something returns False
            # when we're finished with client
            # break
        data = connstream.recv(1024)
    # finished with client


context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=CERT, keyfile=KEY)

bindsocket = socket.socket()
bindsocket.bind((HOST, PORT))
bindsocket.listen(5)

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = context.wrap_socket(newsocket, server_side=True)
    try:
        deal_with_client(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()
