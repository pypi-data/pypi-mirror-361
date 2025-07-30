from . import requests
from .network import tcprequest as tcp
from .core import marker
import json


def get_markers(args=None):
    aw = tcp.TCPRequest(requests.GET_MARKERS_EX_REQUEST)
    res = []
    json_string = ''
    if args is not None:
        json_string = json.dumps(args)
    aw.sendString(json_string)
    if aw.waitForResponse() == -1:
        return res
    response = aw.response()
    nmarkers: int = response.readInt32()
    if nmarkers == 0:
        return res
    aw.waitForResponse()
    for i in range(0, nmarkers):
        m = marker.Marker()
        m.label = response.readQString()
        m.position = response.readFloat()
        m.duration = response.readFloat()
        m.value = response.readFloat()
        m.targets = response.readQStringList()
        res.append(m)
    return res
