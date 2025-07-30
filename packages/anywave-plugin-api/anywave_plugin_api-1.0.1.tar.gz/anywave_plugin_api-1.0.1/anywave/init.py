import anywave


def init(argv):
    _, pid, port = argv
    anywave.pid = int(pid)
    anywave.port = int(port)
