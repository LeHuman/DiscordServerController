#! /usr/bin/python3

import json
import socket
import urllib.request
from enum import Enum
import time

# HOST = "koolkidz.club"
HOST = "99.127.217.73"
PORT = 4578
TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/" + TARGET_SERVER


class Command(Enum):
    triggerOn = "15".encode()
    triggerOff = "12".encode()  # is this a good idea?
    check = "8".encode()


def getAltStatus():
    with urllib.request.urlopen(API_URL) as url:
        data = json.loads(url.read().decode())
        print(data["hostname"] + " is Online:" + data["online"])


def query(cmd):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((HOST, PORT))
            s.send(cmd.value)
            print(s.recv(256).decode())
            s.close()
            return 1
    except:
        print("Error connecting to command server!")
        return 0
