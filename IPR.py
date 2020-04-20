from enum import Enum
import os
import json
import time
import logging
import logging.handlers
import logging.config
from threading import Thread

IPFILE = "IPRecord.json"
USEFILE = False  # if we are unable to write to file disable it
UPDATETIME = 30  # period to update IP JSON
SPAMLENGTH = 2  # length in sec between what would be considered spam
SPAMMAX = 5  # number of times before spam is detected
SPAMRESET = 10  # time to reset spam counter
UPDATE = False
IPRecord = {}

logging.config.fileConfig(fname="log_config.conf", disable_existing_loggers=False)
log = logging.getLogger(__name__)


class IPstate(Enum):
    accept = 0
    banShort = 60  # 1 Min
    banMed = 7200  # 2 Hrs
    banLong = 432000  # 5 days
    banIndefinite = -1


IPlevel = (
    IPstate.accept,
    IPstate.banShort,
    IPstate.banMed,
    IPstate.banLong,
    IPstate.banIndefinite,
)


def JSONUpdate():
    log.info("Running update thread")
    global UPDATE
    while USEFILE:
        if UPDATE:
            updateIPFile()
            log.debug("IP record updated")
            UPDATE = False
        time.sleep(UPDATETIME)
    log.debug("Update thread stopped")


def startJSONThread():
    update_thread = Thread(target=JSONUpdate)
    update_thread.daemon = True
    update_thread.start()


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


def updateIPFile():
    global USEFILE
    if USEFILE:
        try:
            with open(IPFILE, "w+") as f:
                string = json.dumps(IPRecord, cls=IPEncoder, indent=4, sort_keys=True)
                f.write(string)
            return
        except IOError:
            log.error("Error opening/making IP record file")
        except TypeError as e:
            log.error(e)
        log.warning("Disabling file usage")
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
            log.debug("Loaded recorded addresses")
        else:
            with open(IPFILE, "w") as _:
                log.warning("Address file is empty")
        USEFILE = True
        startJSONThread()
        return
    except IOError:
        log.error("Error opening/making inital file")
    except AttributeError:
        log.error("Error interpreting inital file values")
    except json.decoder.JSONDecodeError:
        log.error("Error decoding inital file")
    log.warning("Disabling file usage")
    USEFILE = False


def __setIP(address, state=IPstate.accept):
    try:
        state = IPstate(state)
    except ValueError as e:
        log.error(e)
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
        log.warning(
            "Spam detected: "
            + str(address)
            + " Level:"
            + str(IPRecord[address]["level"])
        )


def __updateIP(address):  # called whenever a new or returning ip connects
    if address in IPRecord:
        __spamCheck(address)
        __touch(address)
        log.info("Returning IP: " + str(address))
    else:
        log.info("New IP: " + str(address))
        __setIP(address)


# IMPROVE: add ip to hosts or somthin? and then periodicly check who gets unbanned instead of waiting for them to reconnect
def checkIP(address):
    global UPDATE
    UPDATE = True
    stradd = str(address)
    log.debug("Checking IP: " + stradd)
    if address in IPRecord:
        level = IPlevel[IPRecord[address]["level"]]
        if IPRecord[address]["state"] == IPstate.banIndefinite:
            log.debug("IP: " + stradd + " Is permenantly banned")
            return False
        elif IPRecord[address]["state"] == IPstate.accept:
            __updateIP(address)
            log.debug("IP: " + stradd + " Is good to go")
            return True
        elif int(time.time()) - IPRecord[address]["time"] > level.value:
            __setIP(address)
            __updateIP(address)
            log.debug("IP: " + stradd + " Is unbanned")
            return True
        else:
            log.debug("IP: " + stradd + " Is currently banned")
            __touch(address)
            return False
    else:
        __updateIP(address)
    return True


init()
