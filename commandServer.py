VERSION = "1.0.0"
HOST = "192.168.1.217"
PORT = 4578
CERT = "cert.pem"
KEY = "priv.key"
RESTARTS = 5
TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/" + TARGET_SERVER
print("\n----------------------------------------------")
print("Command SSL Socket Server", VERSION)
print("----------------------------------------------")
print("HOST: ", HOST)
print("PORT: ", PORT)
print("TARGET SERVER: ", TARGET_SERVER)
print("----------------------------------------------\n")

import logging
import logging.handlers
import logging.config
import socket
import ssl
import time
from datetime import datetime
from enum import Enum
from threading import Thread

import IPR

logging.config.fileConfig(fname="log_config.conf", disable_existing_loggers=False)
log = logging.getLogger("root")


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

    log.debug("Recieved command: " + str(cmd))

    if cmd == Command.check.value:
        # return statusString[SERVERSTATUS]
        return Status(SERVERSTATUS)

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
        self.straddr = str(self.addr[0]) + ":" + str(self.addr[1]) + " : "
        log.debug("New client thread: " + str(self.addr[0]) + ":" + str(self.addr[1]))
        self.start()

    def msg(self, message):
        self.sock.send(message.encode())
        log.debug(self.straddr + str(message))

    def end(self):
        log.debug(self.straddr + "Closing socket and thread")
        self.sock.close()
        self._running = False

    def run(self):
        recieve = self.sock.recv(256).decode()
        try:
            recieve = int(recieve)
        except:
            self.msg("Bad Command")
            log.warning(self.straddr + "Bad command recieved: " + recieve)
            self.end()
            return

        self.msg(order(recieve))
        self.end()


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert.pem", "priv.key")


def socketListen():
    log.info("Command server started")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((HOST, PORT))
        sock.listen(5)
        with context.wrap_socket(sock, server_side=True) as ssock:
            while not (
                SERVERSTATUS == Status.TURNING_OFF or SERVERSTATUS == Status.TURNING_ON
            ):
                try:
                    clientsocket, address = ssock.accept()
                    if IPR.checkIP(address[0]):
                        client(clientsocket, address)
                    else:
                        log.warning("Blocked: " + address[0])
                except OSError as e:
                    print(e)


def newThread(trgt):
    thread = Thread(target=trgt)
    thread.daemon = True
    thread.start()
    return thread


while True:
    time.sleep(60)
    socketThread = newThread(socketListen)
    if not socketThread.is_alive():
        if RESTARTS == 0:
            log.critical("Max restarts has been hit, server must be manually restared")
            break
        RESTARTS -= 1
        log.error("Server seems to have crashed... Attempting restart")

# TODO: how are we actually turning the server on?
