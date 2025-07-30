class Marker:
    """description of class"""

    def __init__(self, label='', position=0., value=0., duration=0., colour="#000000"):
        self.label = label
        self.position = position
        self.duration = duration
        self.value = value
        self.colour = colour
        self.targets = []

    def print(self):
        print("label=", self.label)
        print("position=", self.position)
        print("duration=", self.duration)
        print("value=", self.value)
        print("targets=", self.targets)
        print("colour=", self.colour)

    def set_targets(self, targets):
        self.targets = targets
