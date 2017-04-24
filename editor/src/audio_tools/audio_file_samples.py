import moviepy.editor as movie_editor
import numpy
from ..commons import *
from audio_utils import *

class AudioFileSamples(object):
    def __init__(self, filename):
        self.filename = filename

    def get_all_samples(self):
        audioclip = movie_editor.AudioFileClip(self.filename)
        buffersize = 1000
        samples = audioclip.to_soundarray(buffersize=buffersize)\
                                .transpose().astype(numpy.float32)
        return samples

    def load_samples(self):
        audioclip = movie_editor.AudioFileClip(self.filename)
        buffersize = 1000
        samples = audioclip.to_soundarray(buffersize=buffersize)\
                                .transpose().astype(numpy.float32)

        self.samples = samples
        self.sample_rate = audioclip.fps
        self.duration = audioclip.duration
        self.channels = audioclip.nchannels


    def set_samples(self, samples):
        self.samples = samples
        self.duration = samples.shape[1]*1.0/self.sample_rate

    def get_x_min_max(self):
        return [0, self.duration]

    def get_y_min_max(self):
        return [-1.0, 1.0]

    def get_y_base(self):
        return 0.0

    def get_segment_count(self):
        return self.samples.shape[0]

    def get_sample_at_x(self, segment_index, x):
        sample_index = int(x*self.sample_rate)
        if sample_index<0 or sample_index>= self.samples.shape[1]:
            return None
        return self.samples[segment_index, sample_index]

    def get_samples_in_between(self, start_x=None, end_x=None, padded=False):
        if start_x is not None and end_x is not None:
            st = max(0, int(start_x*self.sample_rate))
            et = min(int(end_x*self.sample_rate), self.samples.shape[1])
            samples = self.samples[:, st:et]
            if padded:
                if st>0:
                    samples = numpy.concatenate(
                                (numpy.zeros((samples.shape[0], st), dtype="f"), samples), axis=1)
                if et<self.samples.shape[1]:
                    samples = numpy.concatenate((samples, numpy.zeros(
                        (samples.shape[0], self.samples.shape[1]-et), dtype="f")), axis=1)
        else:
            samples = self.samples[:, :]
        return samples

    def apply_y_mult_replace(self, start_x, end_x, mult, thresholds):
        start_index = int(start_x*self.sample_rate)
        end_index = int(end_x*self.sample_rate)

        start_index = max(0, start_index)
        end_index = min(end_index, self.samples.shape[1])

        self.samples = sample_segment_mult_replace(
                self.samples, start_index, end_index, mult, thresholds)

    def replace_samples(self, start_end_x, new_samples):
        if start_end_x:
            start_x, end_x = start_end_x[:]
            start_index = int(start_x*self.sample_rate)
            end_index = int(end_x*self.sample_rate)

            start_index = max(0, start_index)
            end_index = min(end_index, self.samples.shape[1])
        else:
            start_index = 0
            end_index = self.samples.shape[1]-1
        pre_samples = self.samples[:, :start_index]
        post_samples = self.samples[:, end_index+1:]
        self.samples = numpy.concatenate((pre_samples, new_samples, post_samples), axis=1)
        self.duration = self.samples.shape[1]*1.0/self.sample_rate

