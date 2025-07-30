from PyQt5 import QtCore, QtNetwork
import anywave
import json

"""
"""
# constants
STATUS_SUCCESS = 0
STATUS_FAILED = 1
SIZE_INT = 4


class TCPRequest:
    WAIT_TIME_OUT = 3000000  # 300s socket time out

    def __init__(self, request):
        self.request = request
        self.socket = QtNetwork.QTcpSocket()
        self.size = QtCore.QByteArray()
        self.data = QtCore.QByteArray()
        self.streamData = QtCore.QDataStream(self.data, QtCore.QIODevice.WriteOnly)
        self.streamData.setVersion(QtCore.QDataStream.Version.Qt_4_4)
        self.streamSize = QtCore.QDataStream(self.size, QtCore.QIODevice.WriteOnly)
        self.streamSize.setVersion(QtCore.QDataStream.Version.Qt_4_4)
        self.streamResponse = QtCore.QDataStream(self.socket)
        self.streamResponse.setVersion(QtCore.QDataStream.Version.Qt_4_4)
        self.status = STATUS_SUCCESS
        self.connect()

    def response(self):
        stream = QtCore.QDataStream(self.socket)
        stream.setVersion(QtCore.QDataStream.Qt_4_4)
        return stream

    def connect(self):
        self.socket.connectToHost(anywave.host, anywave.port)
        if not self.socket.waitForConnected():
            self.status = STATUS_FAILED
            error = "Unable to connect to AnyWave: " + self.socket.errorString()
            raise Exception(error)
        self.status = STATUS_SUCCESS

    def clear(self):
        self.data.clear()
        self.size.clear()
        self.streamData.device().reset()
        self.streamSize.device().reset()

    def waitForResponse(self):
        while self.socket.bytesAvailable() < 4:
            if not self.socket.waitForReadyRead(self.WAIT_TIME_OUT):
                return -1
        stream = QtCore.QDataStream(self.socket)
        stream.setVersion(QtCore.QDataStream.Qt_4_4)
        status = stream.readInt32()
        if status == -1:
            error = stream.readQString()
            raise Exception(error)
        # get size of data
        while self.socket.bytesAvailable() < 4:
            if not self.socket.waitForReadyRead(self.WAIT_TIME_OUT):
                raise Exception('Nothing to read from socket.')
        size = stream.readInt32()
        # wait for all data to be available
        while self.socket.bytesAvailable() < size:
            if not self.socket.waitForReadyRead(self.WAIT_TIME_OUT):
                size = -1
        if size == -1:
            raise Exception('Data waiting timed out.')
        return size

    def simpleRequest(self):
        # arg is a string that could be empty
        if not self.status == STATUS_SUCCESS:
            raise Exception('not connected to AnyWave')
        self.clear()
        self.streamSize.writeInt32(anywave.pid)
        self.streamSize.writeInt32(SIZE_INT)
        self.streamSize.writeInt32(self.request)
        self.socket.write(self.size)
        if not self.socket.waitForBytesWritten():
            raise Exception('Error while sending request to AnyWave')
        return True

    # sendRequest() send a request with parameters a json string.
    # the string can be none or empty
    def sendRequest(self, args):
        # args must be a dict
        if self.status is not STATUS_SUCCESS:
            raise Exception('Sending request while not connected to AnyWave')
        json_string = json.loads(args)
        self.clear()
        self.streamSize.writeInt32(anywave.pid)
        self.streamSize.writeInt32(int(len(json_string) + SIZE_INT))
        self.streamSize.writeInt32(self.request)
        self.streamData.writeQString(json_string)
        self.socket.write(self.size)
        self.socket.write(self.data)
        if not self.socket.waitForBytesWritten():
            raise Exception('Error while sending request to AnyWave')
        return True

    # sendString() will only send a string to AnyWave
    # the string can be a text message or a json string depending on the command
    def sendString(self, string: str):
        if self.status is not STATUS_SUCCESS:
            raise Exception('Sending request while not connected to AnyWave')
        self.clear()
        self.streamSize.writeInt32(anywave.pid)
        self.streamSize.writeInt32(int(len(string) + SIZE_INT))
        self.streamSize.writeInt32(self.request)
        self.streamData.writeQString(string)
        self.socket.write(self.size)
        self.socket.write(self.data)
        if not self.socket.waitForBytesWritten():
            raise Exception('Error while sending request to AnyWave')
        return True

    # sendData() will send binary data to anywave.
    # data must be bytes
    def sendData(self, data):
        # data must be a bytes, not a json string
        if self.status is not STATUS_SUCCESS:
            raise Exception('Sending request while not connected to AnyWave')
        if not isinstance(data, bytes):
            raise Exception('argument must be of type bytes')
        self.clear()
        # use a qbyte array to send the data
        self.streamSize.writeInt32(anywave.pid)
        self.streamSize.writeInt32(int(len(data) + SIZE_INT))
        self.streamSize.writeInt32(self.request)
        self.streamData.writeBytes(data)
        self.socket.write(self.size)
        self.socket.write(self.data)
        if not self.socket.waitForBytesWritten():
            raise Exception('Error while sending request to AnyWave')
        return True
