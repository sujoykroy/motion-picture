import moviepy.editor as movie_editor
import numpy
from audio_segment import AudioSegment

class AudioFileSegment(AudioSegment):
    def __init__(self, filename):
        AudioSegment.__init__(self, start_at=0, duration=0)
        self.filename = filename
        self.start_at = 0
        self.audio_clip = movie_editor.AudioFileClip(self.filename)
        self.sample_rate = self.audio_clip.fps
        self.duration = self.audio_clip.duration

    def get_start_at(self):
        return self.start_at

    def get_duration(self):
        return self.duration

    def get_samples_in_between(self, start_time, end_time):
        if start_time<0:
            start_time = 0
        if end_time>self.duration:
            end_time = self.duration
        tt = numpy.arange(start_time, end_time, 1./self.sample_rate)
        samples = self.audio_clip.to_soundarray(tt).transpose().astype(numpy.float32)
        return samples

