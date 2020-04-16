import socket
import time
from datetime import datetime
from enum import Enum
from threading import Thread

openSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# HOST = "192.168.1.217"
HOST = "99.127.217.73"
PORT = 4578
TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/" + TARGET_SERVER
print("HOST: ", HOST)
print("PORT: ", PORT)
print("TARGET SERVER: ", TARGET_SERVER)
openSocket.bind((HOST, PORT))

statusString = {
    10: "ON",
    5: "TURNING ON",
    2: "TURNING OFF",
    0: "OFF",
}


class Status(Enum):
    ON = 10
    TURNING_ON = 5
    TURNING_OFF = 2
    OFF = 0


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

    if cmd == Command.check:
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
        print("New Client:", socket.getpeername())
        self.start()

    def msg(self, message):
        print(message)
        self.sock.send(bytes(message, "utf-8"))

    def end(self):
        self.sock.send(b"Goodbye")
        self.sock.close()
        

    def run(self):
        recieve = self.sock.recv(4096).decode()
        try:
            recieve = int(recieve)
        except:
            self.msg("Bad Command")
            self.end()
            return

        self.msg(order(recieve))
        self.end()


def socketLoop():
    openSocket.listen(2)
    print("Command server started")
    while not(SERVERSTATUS == Status.TURNING_OFF or SERVERSTATUS == Status.TURNING_ON):
        clientsocket, address = openSocket.accept()
        client(clientsocket, address)
        time.sleep(1)

while 1:
    socketLoop()
    # TODO: how are we turning on the server?
