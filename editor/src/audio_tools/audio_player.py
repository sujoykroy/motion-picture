import threading, numpy, time, Queue
from audio_jack import AudioJack
from audio_fft import AudioFFT
from freq_band import FreqBand

class AudioPlayer(threading.Thread):
    def __init__(self, buffer_mult):
        threading.Thread.__init__(self)
        self.should_stop = False
        self.period = .1
        audio_jack = AudioJack.get_thread()
        if audio_jack:
            self.audio_queue = audio_jack.get_new_audio_queue()
            self.buffer_size = audio_jack.buffer_size*buffer_mult
            self.sample_rate = audio_jack.sample_rate
        else:
            self.buffer_size = 10
            self.sample_rate = 44100.
        self.audio_segments = []
        self.segment_lock = threading.RLock()
        self.duration = 0
        self.t = 0.
        self.last_t = 0.
        self.buffer_time = self.buffer_size*1.0/self.sample_rate

        self.sample_times = numpy.arange(0, self.buffer_size)*1.0/self.sample_rate
        self.sample_times = self.sample_times[:self.buffer_size]
        self.freq_bands = []
        self.audio_fft = None
        self.store_fft = False
        self.loop = True

    def set_loop(self, bool_value):
        self.loop = bool_value

    def add_segment(self, segment, current_time_at=False):
        self.segment_lock.acquire()
        if current_time_at:
            segment.start_at = self.t
        self.audio_segments.append(segment)
        self.compute_duration()
        self.segment_lock.release()

    def remove_segment(self, segment):
        self.segment_lock.acquire()
        self.audio_segments.remove(segment)
        self.compute_duration()
        self.segment_lock.release()

    def compute_duration(self):
        duration = 0
        for audio_segment in self.audio_segments:
            spread = audio_segment.get_start_at() + audio_segment.get_duration()
            if spread>duration:
                duration = spread
        self.duration = duration

    def clear_queue(self):
        AudioJack.get_thread().clear_audio_queue(self.audio_queue)

    def reset_time(self):
        self.t = 0

    def run(self):
        while not self.should_stop:
            full_buffer_size = self.buffer_size
            final_samples = None
            st = time.time()
            while not self.should_stop and \
                 (final_samples is None or \
                   final_samples.shape[1]<full_buffer_size) \
                                            and self.audio_segments:
                joined_samples = None
                buffer_time = min(self.buffer_time, self.duration-self.t)
                buffer_size = int(buffer_time*self.sample_rate)

                for s in range(len(self.audio_segments)):
                    self.segment_lock.acquire()
                    if s<len(self.audio_segments):
                        audio_segment = self.audio_segments[s]
                    else:
                        audio_segment = None
                    self.segment_lock.release()
                    if audio_segment is None:
                        continue
                    start_at = audio_segment.get_start_at()
                    duration = audio_segment.get_duration()
                    if self.t+buffer_time<start_at or self.t>start_at+duration:
                        continue

                    pre_blank_period = start_at - self.t
                    post_blank_period = self.t+buffer_time-start_at-duration

                    start_time = max(self.t-start_at, 0)
                    end_time = min(self.t+buffer_time-start_at, duration)

                    samples = audio_segment.get_samples_in_between(start_time, end_time)
                    channels = samples.shape[0]
                    sample_count = samples.shape[1]

                    pre_blank_sample_count = int(pre_blank_period*self.sample_rate)
                    if pre_blank_sample_count>0:
                        pre_blank = numpy.zeros((channels, pre_blank_sample_count), dtype=numpy.float32)
                        samples = numpy.concatenate((pre_blank, samples), axis=1)

                    post_blank_sample_count = buffer_size - samples.shape[1]
                    if post_blank_sample_count>0:
                        post_blank = numpy.zeros((channels, post_blank_sample_count), dtype=numpy.float32)
                        post_blank = post_blank.reshape(channels, -1).astype(numpy.float64)
                        samples = numpy.concatenate((samples, post_blank), axis=1)
                    samples = samples[:, :buffer_size]
                    if joined_samples is None:
                        joined_samples = samples
                    else:
                        joined_samples += samples
                    #time.sleep(.01)
                if final_samples is None:
                    final_samples = joined_samples
                else:
                    try:
                        final_samples = numpy.concatenate((final_samples, joined_samples), axis=1)
                    except ValueError as e:
                        print e

                self.t += buffer_time
                while self.loop and self.t>=self.duration:
                    self.t -= self.duration
            if final_samples is not None and final_samples.shape[1]>1:
                max_amp = numpy.amax(final_samples)
                if max_amp>1.0:
                    final_samples = final_samples/max_amp

                if self.freq_bands:
                    audio_fft = None
                    modified = False
                    for band in self.freq_bands:
                        if band.mult==1:
                            continue
                        if audio_fft is None:
                            audio_fft = AudioFFT(final_samples, self.sample_rate)
                        audio_fft.apply_freq_band(band)
                        modified = True

                    if modified:
                        final_samples = audio_fft.get_reconstructed_samples()
                    if self.store_fft:
                        self.audio_fft = audio_fft
                    audio_fft = None
                else:
                    if self.store_fft:
                        self.audio_fft = AudioFFT(final_samples, self.sample_rate)
                self.last_t = self.t
                try:
                    self.audio_queue.put(final_samples.astype(numpy.float32), block=False)
                except Queue.Full:
                    pass

            if not self.loop:
                s = 0
                self.segment_lock.acquire()
                while s<len(self.audio_segments):
                    audio_segment = self.audio_segments[s]
                    if self.t>audio_segment.start_at+audio_segment.duration:
                        self.audio_segments.remove(audio_segment)
                        self.compute_duration()
                        s -= 1
                    s += 1
                self.segment_lock.release()

            time.sleep(max(.01, self.period-(time.time()-st)))
        audio_jack = AudioJack.get_thread()
        if audio_jack:
            audio_jack.remove_audio_queue(self.audio_queue)
        self.audio_queue = None

    def close(self):
        self.should_stop = True
        if self.is_alive():
            self.join()
