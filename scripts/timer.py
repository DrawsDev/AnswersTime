from time import time as t

class Timer:
    def __init__(self, time=1.0, loop=False) -> None:
        self._time = time
        self._loop = loop
        self.reset()
    
    @property
    def expired(self) -> bool:
        result = t() - self._start_t > self._time
        if result & self._loop: self.reset()
        return result

    def reset(self) -> None:
        self._start_t = t()
    
    def stop(self) -> None:
        self._start_t = t() - self._time
