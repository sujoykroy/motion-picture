class AudioSegment(object):
    def __init__(self, start_at, duration):
        self.start_at = start_at
        self.duration = duration

    def get_start_at(self):
        return self.start_at

    def get_duration(self):
        return self.duration
