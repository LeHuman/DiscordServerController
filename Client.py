#! /usr/bin/python3

import json
import socket
import ssl
import urllib.request
from enum import Enum
import time
from threading import Thread

HOST = "www.koolkidz.club"
PORT = 4578
TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/" + TARGET_SERVER
context = ssl.SSLContext(ssl.PROTOCOL_TLS)


class Command(Enum):
    triggerOn = "15".encode()
    triggerOff = "12".encode()  # is this a good idea?
    check = "8".encode()


def getAltStatus():
    with urllib.request.urlopen(API_URL) as url:
        data = json.loads(url.read().decode())
        print(data["hostname"], "is online" if data["online"] else "is offline")
        if data["motd"]:
            print(data["motd"]["clean"])
        if data["players"]:
            print("Players online:", data["players"]["online"])


def query(cmd):
    try:
        with socket.create_connection((HOST, PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=HOST) as ssock:
                ssock.settimeout(2)
                ssock.send(cmd.value)
                print(ssock.recv(256).decode())
                ssock.close()
                return 1
    except ssl.SSLError as e:
        print(e)
    except ConnectionResetError as e:
        print(e)

class spam2(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()
    def run(self):
        spam()
        for _ in range(20):
            query(Command.triggerOff)
            query(Command.triggerOn)

class spam(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()
    def run(self):
        spam2()
        for _ in range(20):
            query(Command.triggerOff)
            query(Command.triggerOn)

spam()
query(Command.triggerOff)