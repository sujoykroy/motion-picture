import time

class TimerClock(object):
    def __init__(self):
        self.started_at = None
        self.paused = True
        self.elapsed = 0.

    def start(self):
        self.started_at = time.time()
        self.paused = False

    def pause(self):
        if self.paused:
            return
        self.elapsed += time.time()-self.started_at
        self.paused = True

    def reset(self):
        self.elapsed = 0.

    def get_duration(self):
        return self.elapsed + (time.time()-self.started_at)
