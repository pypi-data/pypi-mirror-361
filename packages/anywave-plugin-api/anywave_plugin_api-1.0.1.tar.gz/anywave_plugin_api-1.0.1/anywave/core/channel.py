
import numpy

class Channel:
    def __init__(self):
        name = ''
        ref = ''
        type = ''
        sr = 0.
        lp = 0.
        hp = 0.
        notch = 0.
        data = numpy.empty(1, numpy.float32)
        unit = ''

    def full_name(self):
        if self.ref == '':
            return self.name
        return self.name + '-' + self.ref

