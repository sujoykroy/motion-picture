import moviepy.editor as movie_editor
import numpy
from ..audio_tools import *

class AudioClipGenerator(movie_editor.AudioClip):
    def __init__(self, time_offset, slice_offset, scale, duration, time_slice):
        movie_editor.AudioClip.__init__(self, make_frame=None, duration=duration)
        self.time_offset = time_offset
        self.slice_offset = slice_offset
        self.nchannels=2
        self.scale = scale
        self.time_slice = time_slice

    def make_frame(self, t):
        final_samples = None
        filename = self.time_slice.prop_data["av_filename"]
        if not filename or filename == "//":
            return numpy.zeros((t.shape[0], 2), dtype="f")
        t = (t*self.scale) + self.slice_offset
        t = self.time_slice.value_at(t)
        audio_file = AudioFileCache.get_file(filename)
        samples = audio_file.get_samples(at=t).copy()
        return samples.T

    def __repr__(self):
        return "AudioClip(time_offset={0}, scale={1}, duration={2})".format(
                self.time_offset, self.scale, self.duration)

