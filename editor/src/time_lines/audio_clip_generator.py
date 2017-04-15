import moviepy.editor as movie_editor
import numpy

class AudioClipGenerator(movie_editor.AudioClip):
    def __init__(self, audio_shape, time_slice):
        movie_editor.AudioClip.__init__(self, make_frame=None, duration=time_slice.duration)
        self.nchannels=2
        self.audio_shape = audio_shape
        self.time_slice = time_slice

    def make_frame(self, t):
        scale = (self.time_slice.end_value-self.time_slice.start_value)/self.time_slice.duration
        final_samples = None
        self.audio_shape.set_audio_path(self.time_slice.prop_data["av_filename"])
        if isinstance(t, int):
            final_samples = self.audio_shape.get_sample(at=self.time_slice.start_value+t*scale)
            final_samples = final_samples.reshape(self.nchannels, -1)
        else:
            for ti in t:
                samples = self.audio_shape.get_sample(at=self.time_slice.start_value+ti*scale)
                samples = samples.reshape(self.nchannels, -1)
                if final_samples is None:
                    final_samples = samples
                else:
                    final_samples = numpy.concatenate((final_samples, samples), axis=1)
        return final_samples.T

