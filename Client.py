#! /usr/bin/python3

import json
import socket
import urllib.request

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# HOST = "192.168.1.217"
HOST = "99.127.217.73"
PORT = 4578
TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/" + TARGET_SERVER
s.connect((HOST, PORT))

# with urllib.request.urlopen(API_URL) as url:
#     data = json.loads(url.read().decode())
#     print(data["online"])
#     print(data["hostname"])

s.send("15".encode())
data = ""
data = s.recv(4096).decode()
print(data)

s.close()
