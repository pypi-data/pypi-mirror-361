from . import requests
from .network import tcprequest as tcp
from PyQt5 import QtCore


def send_markers(markers):
    MAX_MARKERS_AT_ONCE = 1000
    if type(markers) is not list:
        raise Exception('arguments of send_markers must be a list of Markers')
    aw = tcp.TCPRequest(requests.SEND_MARKERS_REQUEST)
    nmarkers: int = int(len(markers))
    data = QtCore.QByteArray()
    stream_data = QtCore.QDataStream(data, QtCore.QIODevice.WriteOnly)
    stream_data.setVersion(QtCore.QDataStream.Version.Qt_4_4)
    counter = 0
    stream_data.writeInt32(nmarkers)
    for i in range(0, nmarkers):
        stream_data.writeQString(markers[i].label)
        stream_data.writeQString(markers[i].colour)
        stream_data.writeFloat(markers[i].position)
        stream_data.writeFloat(markers[i].duration)
        stream_data.writeFloat(markers[i].value)
        stream_data.writeQStringList(markers[i].targets)
    aw.sendData(bytes(data))
    aw.waitForResponse()  # wait for anywave to acknowledge

