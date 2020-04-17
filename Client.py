#! /usr/bin/python3

import json
import socket
import ssl
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
        print(data["hostname"], "is online" if data["online"] else "is offline")
        if data["motd"]:
            print(data["motd"]["clean"])
        if data["players"]:
            print("Players online:", data["players"]["online"])


def query(cmd):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            ws = ssl.wrap_socket(
                s, ssl_version=ssl.PROTOCOL_TLSv1, ciphers="ADH-AES256-SHA"
            )
            ws.connect((HOST, PORT))
            ws.send(cmd.value)
            print(ws.recv(256).decode())
            ws.close()
            return 1
    except:
        print("Error connecting to command server!")
        return 0


def handle(conn):
    conn.write(b"GET / HTTP/1.1\n")
    print(conn.recv().decode())


# sock = socket.socket(socket.AF_INET)
# sock.settimeout(10)
# context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
# context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # optional
# conn = context.wrap_socket(sock, server_hostname=HOST)
# try:
#     conn.connect((HOST, PORT))
#     handle(conn)
# finally:
#     conn.close()

context = ssl.create_default_context()
conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=HOST)
conn.connect((HOST, PORT))
cert = conn.getpeercert()
print(cert)