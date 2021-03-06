import moviepy.editor as movie_editor
import numpy
from ..audio_tools import AudioBlock, AudioFileBlock, AudioFileBlockCache

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
        filename = self.time_slice.prop_data.get("audio_path")
        if not filename:
            filename = self.time_slice.prop_data.get("video_path")
        if not filename or filename == "//":
            return numpy.zeros((t.shape[0], 2), dtype="f")
        t = (t*self.scale) + self.slice_offset
        t = self.time_slice.value_at(t)
        audio_block = AudioFileBlock.get_for_filename(filename)
        if len(audio_block.samples) == 0:
            return numpy.zeros((t.shape[0], 2), dtype="f")

        t = (t*AudioBlock.SampleRate)
        if isinstance(t, numpy.ndarray):
            t = t.astype(numpy.int)
        else:
            t = int(t)
        audio_block.load_samples()
        t = numpy.where(t>=audio_block.samples.shape[0], 0, t)
        samples = audio_block.samples[t,:].copy()
        return samples

    def get_samples(self, frame_count):
        t= numpy.linspace(0, self.duration, frame_count, endpoint=False)
        samples = self.make_frame(t)
        if samples.shape[0]<frame_count:
            blank_data = numpy.zeros((frame_count-samples.shape[0], samples.shape[1]))
            samples = numpy.append(samples, blank_data, axis=0)
        return samples

    def __repr__(self):
        text =  "AudioClip(time_offset={0}, scale={1}, "
        text += "duration={2}, slice_offset={3})"
        return text.format(self.time_offset, self.scale,
                           self.duration, self.slice_offset)

