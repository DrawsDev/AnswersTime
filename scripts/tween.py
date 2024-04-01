from enum import Enum
from time import time
import pytweening

class TweenStyle(Enum):
    Linear = "linear"
    SineIn = "easeInSine"
    SineOut = "easeOutSine"
    SineInOut = "easeInOutSine"
    BackIn = "easeInBack"
    BackOut = "easeOutBack"
    BackInOut = "easeInOutBack"
    QuadIn = "easeInQuad"
    QuadOut = "easeOutQuad"
    QuadInOut = "easeInOutQuad"
    QuartIn = "easeInQuart"
    QuartOut = "easeOutQuart"
    QuartInOut = "easeInOutQuart"
    QuintIn = "easeInQuint"
    QuintOut = "easeOutQuint"
    QuintInOut = "easeInOutQuint"
    BounceIn = "easeInBounce"
    BounceOut = "easeOutBounce"
    BounceInOut = "easeInOutBounce"
    ElasticIn = "easeInElastic"
    ElasticOut = "easeOutElastic"
    ElasticInOut = "easeInOutElastic"
    ExpoIn = "easeInExpo"
    ExpoOut = "easeOutExpo"
    ExpoInOut = "easeInOutExpo"
    CircIn = "easeInCirc"
    CircOut = "easeOutCirc"
    CircInOut = "easeInOutCirc"
    CubicIn = "easeInCubic"
    CubicOut = "easeOutCubic"
    CubicInOut = "easeInOutCubic"

class Tween:
    def __init__(self,
                 start: float = 0.0,
                 end: float = 1.0,
                 duration: int = 1,
                 style: TweenStyle = TweenStyle.Linear,
                 repeats: int = 1,
                 reverses: bool = False
                 ) -> None:
        
        self._init_start = start
        self._start = start
        self._end = end
        self._duration = duration
        self._style = style.value
        self._repeats = repeats
        self._reverses = reverses
        self._ease = getattr(pytweening, self._style, pytweening.linear)

        self._start_time = 0
        self._pause_time = 0
        self._playing = False
        self._paused = False

        self._value = self._start
        self._step = 0
        self._repeat_count = 1

    @property
    def value(self):
        return self._value

    def play(self):
        if not self._playing:
            self._start_time = time()
            self._playing = True
    
    def pause(self):
        if not self._paused:
            self._pause_time = time()
            self._paused = True
    
    def resume(self):
        if self._paused:
            self._paused = False
            self._start_time += time() - self._pause_time

    def update(self):
        if self._playing and not self._paused:
            now = time()
            passed = now - self._start_time
            self._step = max(min(passed / self._duration, 1.0), 0.0)
            delta = self._end - self._start

            self._value = self._ease(self._step) * delta + self._start

            if self._step >= 1.0:
                if self._reverses:
                    self._start_time = now
                    self._start, self._end = self._end, self._start

                    if self._value == self._init_start:
                        if self._repeats:
                            self._play_again()
                        else:
                            self._playing = False
                else:
                    if self._repeats:
                        self._play_again()
                    else:
                        self._playing = False

    def _play_again(self):
        if self._repeats <= 0:
            self._playing = False
            self.play()
        else:
            if self._repeat_count < self._repeats:
                self._repeat_count += 1
                self._playing = False
                self.play()
            else:
                self._repeat_count = 1
                self._playing = False