from enum import Enum
import os
import json
import time
from threading import Thread

IPFILE = "IPRecord.json"
USEFILE = False  # if we are unable to write to file disable it
UPDATETIME = 10  # period to update IP JSON
SPAMLENGTH = 2  # length in sec between what would be considered spam
SPAMMAX = 5  # number of times before spam is detected
SPAMRESET = 10  # time to reset spam counter
IPRecord = {}


class IPstate(Enum):
    accept = 0
    banShort = 5
    banMed = 10
    banLong = 20
    banIndefinite = -1


IPlevel = (
    IPstate.accept,
    IPstate.banShort,
    IPstate.banMed,
    IPstate.banLong,
    IPstate.banIndefinite,
)


class JSONThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()

    def run(self):
        while True:
            updateIPFile()
            time.sleep(UPDATETIME)


class IPEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, IPstate):
            return {"IPstate": str(obj)}
        return json.JSONEncoder.default(self, obj)


def IPDecode(d):
    if "IPstate" in d:
        _, member = d["IPstate"].split(".")
        return getattr(IPstate, member)
    else:
        return d


def updateIPFile():  # TODO: make this run periodiclly
    global USEFILE
    if USEFILE:
        try:
            with open(IPFILE, "w+") as f:
                string = json.dumps(IPRecord, cls=IPEncoder, indent=4, sort_keys=True)
                f.write(string)
            return
        except IOError:
            print("Error opening/making file")
        except TypeError as e:
            print(e)
        USEFILE = False


def init():
    global USEFILE
    global IPRecord
    try:
        if (
            os.path.isfile(IPFILE)
            and os.access(IPFILE, os.R_OK)
            and os.stat(IPFILE).st_size != 0
        ):
            with open(IPFILE, "r") as f:
                IPRecord = json.load(f, object_hook=IPDecode)
            print("Loaded recorded addresses")
            print(IPRecord)
        else:
            with open(IPFILE, "w") as _:
                print("address file empty")
        USEFILE = True
        return
    except IOError:
        print("Error opening/making file")
    except AttributeError:
        print("Error interpreting file values")
    except json.decoder.JSONDecodeError:
        print("Error decoding file")
    USEFILE = False
    JSONThread()


def __setIP(address, state=IPstate.accept):
    try:
        state = IPstate(state)
    except ValueError as e:
        print(e)
        return

    if address in IPRecord:
        IPRecord[address]["state"] = state
    else:
        IPRecord[address] = {
            "state": state,
            "time": int(time.time()),
            "spam": 0,
            "level": 0,
        }


def __touch(address):
    IPRecord[address]["time"] = int(time.time())


def __spamCheck(address):
    diff = int(time.time()) - IPRecord[address]["time"]
    if diff <= SPAMLENGTH:
        IPRecord[address]["spam"] += 1
    elif diff > SPAMRESET:
        IPRecord[address]["spam"] = 0
    if IPRecord[address]["spam"] > SPAMMAX:
        IPRecord[address]["level"] += 1
        IPRecord[address]["spam"] = 1
        __setIP(address, IPlevel[IPRecord[address]["level"]])
        print("Spam detected:", address, " Level:", IPRecord[address]["level"])


def __updateIP(address):  # called whenever a new or returning ip connects
    if address in IPRecord:
        __spamCheck(address)
        __touch(address)
    else:
        print("New IP:", address)
        __setIP(address)


# IMPROVE: add ip to hosts or somthin? and then periodicly check who gets unbanned instead of waiting for them to reconnect
def checkIP(address):
    if address in IPRecord:
        level = IPlevel[IPRecord[address]["level"]]
        if IPRecord[address]["state"] == IPstate.banIndefinite:
            return False
        elif IPRecord[address]["state"] == IPstate.accept:
            __updateIP(address)
            return True
        elif int(time.time()) - IPRecord[address]["time"] > level.value:
            __setIP(address)
            __updateIP(address)
            return True
        else:
            __touch(address)
            return False
    else:
        __updateIP(address)
    return True


init()
