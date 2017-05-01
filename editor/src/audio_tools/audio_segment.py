class AudioSegment(object):
    def __init__(self, start_at, duration):
        self.start_at = start_at
        self.duration = duration
        self.loop = False

    def set_loop(self, bool_value):
        self.loop = bool_value

    def get_start_at(self):
        return self.start_at

    def get_duration(self):
        return self.duration
