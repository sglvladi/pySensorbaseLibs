import json
import time
from http.client import HTTPConnection

import netifaces as ni

from .global_vars import *


def get_mac_address(interface='wlan0'):
    """
    Return the MAC address of a network interface.

    Parameters
    ----------
    interface: str
        The name of the network interface.

    Returns
    -------
    str
        The MAC address of the network interface.
    """

    mac = "00:00:00:00:00:11"
    try:
        with open(f'/sys/class/net/{interface}/address', 'r') as f:
            mac = f.read().strip()[0:17].upper().replace(":", "-")
    except:
        pass

    return mac


def get_local_ip(interface='wlan0'):
    """
    Return the local IP address of a network interface.

    Parameters
    ----------
    interface: str
        The name of the network interface.

    Returns
    -------
    str
        The local IP address of the network interface.
    """

    return ni.ifaddresses(interface)[ni.AF_INET][0]['addr']


def register_device(reg_key, mac):
    """
    Register a device with the Sensorbase server.

    Parameters
    ----------
    reg_key
    mac

    Returns
    -------

    """
    if reg_key is None:
        raise Exception("Not Authorized")

    payload = {
        "mac": mac,
        "hw_version": "1.0.1",
        "fw_version": "1.0.1",
        "model": "HubMadoka",
        "token": reg_key
    }
    headers = {
        "Accept-Encoding": "gzip,deflate",
        "Content-Type": "application/json",
        "Content-Length": len(json.dumps(payload)),
        "Connection": "Keep-Alive"
    }

    con = HTTPConnection(API_HOST, API_PORT, timeout=10)

    connected = False
    failCount = 0
    while not connected:
        try:
            con.connect()
            connected = True
        except Exception as e:
            # print("Error no internet {}".format(e))
            failCount = failCount + 1
            time.sleep(10 * failCount * failCount)

    # print("Sending Reg Request.. {}".format(mesg))
    con.request("POST", "/v1/hw/regauth", body=json.dumps(payload).encode(), headers=headers)

    resp = con.getresponse()
    payload = resp.readline()
    resp.close()
    j_payload = json.loads(payload.decode())
    return j_payload
