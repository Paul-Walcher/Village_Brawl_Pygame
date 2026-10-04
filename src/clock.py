import time

class Clock:

    #does time in milliseconds

    def __init__(self):

        self._stime = None

    def start(self):

        self._stime = time.perf_counter() * 1000

    def elapsed(self):

        return (time.perf_counter() * 1000 - self._stime)
