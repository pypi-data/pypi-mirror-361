from . import requests
from .network import tcprequest as tcp
import json


def get_props() -> dict:
    aw = tcp.TCPRequest(requests.GET_PROP_REQUEST)
    aw.simpleRequest()
    aw.waitForResponse()
    response = aw.response()
    json_string = response.readQString()
    return json.loads(json_string)
