from . import requests
from .network import tcprequest as tcp
import anywave
import json


def debug_connect(port=None) -> dict:
    if port:
        anywave.port = port
    anywave.pid = -1
    aw = tcp.TCPRequest(requests.CONNECT_DEBUG_REQUEST)
    aw.simpleRequest()
    aw.waitForResponse()
    # we must have a response containing the new pid allocated by anywave
    response = aw.response()
    pid = response.readInt32()
    anywave.pid = pid
    string = response.readQString()
    anywave.properties = json.loads(string)
    return anywave.properties
