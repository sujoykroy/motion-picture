from audio_segment import AudioSegment

class AudioRawSamples(AudioSegment):
    def __init__(self, samples, sample_rate):
        AudioSegment.__init__(self, start_at=0, duration=0)
        self.samples = samples
        self.sample_rate = sample_rate
        self.duration = samples.shape[1]*1.0/self.sample_rate

    def get_samples_in_between(self, start_time, end_time):
        st = int(start_time*self.sample_rate)
        et = min(end_time*self.sample_rate, self.samples.shape[1])
        return self.samples[:, st:et]

    def get_x_min_max(self):
        return [0, self.duration]

    def get_y_min_max(self):
        return [-1.0, 1.0]

    def get_y_base(self):
        return 0.0

    def get_segment_count(self):
        return self.samples.shape[0]

    def get_sample_at_x(self, segment_index, x):
        x = int(x*self.sample_rate)
        if x<0 or x>=self.samples.shape[1]:
            return None
        return self.samples[segment_index, x]
