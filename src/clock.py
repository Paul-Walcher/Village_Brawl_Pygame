import time

class Clock:
    """
    Clock class.
    This class stores the time it was activated via start(),
    then you can get the time in milliseconds that passed since the last
    activation via elapsed()
    """

    #does time in milliseconds

    def __init__(self):
        self._stime = None
        """
        stores the last activated timestamp
        """

    def start(self) -> None:
        """
        stores the current time as a timestamp
        """
        self._stime = time.perf_counter() * 1000

    def elapsed(self) -> float:
        """
        returns the milliseconds elapsed
        since the last start call
        """
        if self._stime is None:
            return 0

        return (time.perf_counter() * 1000 - self._stime)
