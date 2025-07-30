from . import requests
from .network import tcprequest as tcp
import json


def run(args=None) -> dict:
    if args is None:
        return dict()
    aw = tcp.TCPRequest(requests.RUN_REQUEST)
    aw.sendString(json.dumps(args))
    aw.waitForResponse()
    response = aw.response()
    return json.loads(response.readQString())
