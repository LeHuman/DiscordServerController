import json
import socket
import ssl
import urllib.request
from enum import Enum
import time
from threading import Thread
import concurrent.futures
import os

HOST = "www.koolkidz.club"
PORT = 4578
TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/" + TARGET_SERVER
context = ssl.SSLContext(ssl.PROTOCOL_TLS)
DEBUG = False


class Command(Enum):
    turnOn = "15".encode()
    turnOff = "12".encode()  # is this a good idea?
    status = "8".encode()


def log(*args):
    if DEBUG:
        for count, thing in enumerate(args):
            print("{0}. {1}".format(count, thing))


def getAltStatus():
    with urllib.request.urlopen(API_URL) as url:
        data = json.loads(url.read().decode())
        final = (
            TARGET_SERVER
            + " is currently "
            + ("online" if data["online"] else "offline")
        )
        # if "motd" in data:
        #     final += " " + data["motd"]["clean"]
        if "players" in data:
            final += " Players online: " + data["players"]["online"]
        return final


def _newQuery(cmd):
    try:
        with socket.create_connection((HOST, PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=HOST) as ssock:
                ssock.settimeout(5)
                ssock.send(cmd.value)
                msg = ssock.recv(256).decode()
                ssock.close()
                return msg
    except ssl.SSLError as e:
        log(e)
    except ConnectionResetError as e:
        log(e)
    except Exception as e:
        log(e)
        return "There has been an error connecting to the server!"


def newThread(trgt):
    thread = Thread(target=trgt)
    thread.daemon = True
    thread.start()
    return thread


def query(cmd):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_newQuery, cmd)
        result = future.result()
        return result
