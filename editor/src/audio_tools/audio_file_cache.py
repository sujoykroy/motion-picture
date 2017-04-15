import time, numpy
import moviepy.editor as movie_editor

class AudioFileCache(object):
    files = dict()
    access_time_list = []
    total_memory = 0
    MEMORY_LIMIT = 500*1024*1024

    def __init__(self, filename):
        self.filename = filename
        self.last_access_at = None
        self.samples = None

    def load_samples(self):
        self.last_access_at = time.time()
        if self.samples is not None:
            return
        audioclip = movie_editor.AudioFileClip(self.filename)
        self.samples = audioclip.to_soundarray(buffersize=1000)\
                                      .transpose().astype(numpy.float32)
        self.sample_rate = audioclip.fps
        self.duration = audioclip.duration
        AudioFileCache.total_memory  += self.samples.nbytes

    def unload_samples(self):
        if self.samples is not None:
            AudioFileCache.total_memory -= self.samples.nbytes
            self.samples = None
            self.audioclip = None

    def get_sample_at(self, at):
        pos = int(at*self.sample_rate)
        if pos<0 or pos>=self.samples.shape[1]:
            return numpy.zeros((self.samples.shape[0], 1), dtype="f")
        return self.samples[:, pos]

    def get_samples_in_between(self, start_at, end_at):
        start_at = int(start_at*self.sample_rate)
        end_at = int(end_at*self.sample_rate)
        if start_at<0:
            pre_samples = numpy.zeros((self.samples.shape[0], -start_at), dtype="f")
            start_at = 0
        else:
            pre_samples = None
        if end_at> self.samples.shape[1]:
            post_samples = numpy.zeros(
                (self.samples.shape[0], self.samples.shape[1]-end_at), dtype="f")
            end_at = self.samples.shape[1]
        else:
            post_samples = None
        samples = self.samples[:, start_at:end_at]
        if pre_samples:
            samples = numpy.concatenate((pre_samples, samples), axis=1)
        if post_samples:
            samples = numpy.concatenate((samples, post_samples), axis=1)
        return samples

    @staticmethod
    def get_file(filename):
        if filename not in AudioFileCache.files:
            audio_file_cache = AudioFileCache(filename)
            AudioFileCache.files[filename] = audio_file_cache
        else:
            audio_file_cache = AudioFileCache.files[filename]
        sorted_files = sorted(AudioFileCache.files.values(), key=lambda cache: cache.last_access_at)
        while sorted_files and AudioFileCache.total_memory>AudioFileCache.MEMORY_LIMIT:
            first_file = sorted_files[0]
            sorted_files = sorted_files[1:]
            first_file.unload_samples()
        audio_file_cache.load_samples()
        return audio_file_cache
