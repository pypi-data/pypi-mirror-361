from . import requests
from .network import tcprequest as tcp
import json
from .core import channel as channel
import numpy


def get_data(args=None) -> list:
    aw = tcp.TCPRequest(requests.GET_DATA_2_5_10)
    tmp = ''
    res = []
    if args is None:
        pass
    else:
        tmp = json.dumps(args)
    aw.sendString(tmp)
    aw.waitForResponse()
    response = aw.response()
    nChannels = response.readInt32()
    nTimeSelections = response.readInt32()
    if nChannels == 0:
        return res
    channels = []
    for i in range(0, nChannels):
        aw.waitForResponse()
        chan = channel.Channel()
        chan.name = response.readQString()
        chan.type = response.readQString()
        chan.ref = response.readQString()
        chan.sr = response.readFloat()
        chan.hp = response.readFloat()
        chan.lp = response.readFloat()
        chan.notch = response.readFloat()
        chan.unit = response.readQString()
        channels.append(chan)
    aw.waitForResponse()
    for i in range(0, nTimeSelections):
        pos = response.readFloat()
        duration = response.readFloat()
        d = { "channels" : channels , 
             "position" : pos,
             "duration" : duration}
        res.append(d)
    for i in range(0, nTimeSelections):
        aw.waitForResponse()
        nSamples = response.readInt64()
        if nSamples > 0:
            data = numpy.zeros(nSamples, numpy.float32)
            finished = False
            nSamplesRead = 0
            chunkSize = 0
            while not finished:
                aw.waitForResponse()
                chunkSize = response.readInt64()
                if chunkSize == 0:
                    finished = True
                else:
                    for j in range(0, chunkSize):
                        data[j + nSamplesRead] = response.readFloat()
                    nSamplesRead += chunkSize
            res[i]["data"] = data
    return res
