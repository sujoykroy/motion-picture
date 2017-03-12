import wave, numpy, math, Queue

class AudioTimeLine(object):
    ID_SEED = 0

    def __init__(self, filename, start, end):
        self.filename = filename
        self.start = start
        self.end = end
        self.id_num = AudioTimeLine.ID_SEED
        AudioTimeLine.ID_SEED += 1
        self.samples = None
        self.file_duration = 0

        self.load_file()

    def __hash__(self):
        return hash(self.id_num)

    def __eq__(self, other):
        return isinstance(other, AudioTimeLine) and self.id_num == other.id_num

    def __ne__(self, other):
        return not (self == other)


    def load_file(self):
        wavef = wave.open(self.filename, "rb")
        self.file_duration = wavef.getnframes()/wavef.getframerate()

        sample_width = wavef.getsampwidth()
        if sample_width == 1:
            sample_type = numpy.int8
            max_sample_value = math.pow(2,8)
        elif sample_width == 2:
            sample_type = numpy.int16
            max_sample_value = math.pow(2,16)
        elif sample_width == 4:
            sample_type = numpy.int32
            max_sample_value = math.pow(2,32)

        samples = wavef.readframes(wavef.getnframes())
        if len(samples)>100*1024*1024:
            return
        samples = numpy.fromstring(samples, dtype=sample_type)
        samples = samples.reshape((samples.shape[0]/wavef.getnchannels(),
                                    wavef.getnchannels())).astype('f')
        samples = numpy.divide(samples, max_sample_value)
        samples = samples.transpose()

        self.samples = samples
        self.frame_rate = wavef.getframerate()

    def move_to(self, t, audio_queue, duration):
        if self.samples is None:
            return
        s = int(t*self.frame_rate)
        samples = self.samples[:, s: s+int(duration*self.frame_rate)]
        try:
            audio_queue.put(samples, block=False)
        except Queue.Full as e:
            pass

    def get_sample(self, at):
        if self.samples is None:
            return None
        pos = int(at*self.frame_rate)
        if pos>self.samples.shape[1]:
            return None
        return self.samples[:, pos]

    def get_duration(self):
        return self.file_duration

