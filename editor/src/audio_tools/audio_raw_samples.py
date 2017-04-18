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
