import threading, jack, numpy,Queue, time, tempfile, shutil
from audio_file_writer  import *

class AudioJack(threading.Thread):
    _running_thread = None

    @staticmethod
    def get_thread():
        if AudioJack._running_thread is None:
            AudioJack._running_thread = AudioJack()
            AudioJack._running_thread.start()
        return AudioJack._running_thread

    @staticmethod
    def close_thread():
        if AudioJack._running_thread is None:
            return
        jack_thread = AudioJack._running_thread
        jack_thread.should_stop = True
        if jack_thread.is_alive():
            jack_thread.join()
        AudioJack._running_thread = None

    def __init__(self, name="jack"):
        threading.Thread.__init__(self)
        jack_name = "mpa_" + name
        self.should_stop = False
        self.started = False
        self.period = .01
        self.audio_queues = []
        self.record = False
        self.wave_file = None
        self.record_lock = threading.RLock()
        try:
            jack.attach(jack_name)
            jack.activate()
        except jack.UsageError as e:
            pass
        except jack.NotConnectedError as e:
            self.should_stop = True
            self.buffer_size = 0
            self.sample_rate = 1.0
            return

        port_name = "out"
        jack.register_port(port_name+"_1", jack.IsOutput | jack.CanMonitor)
        jack.register_port(port_name+"_2", jack.IsOutput | jack.CanMonitor)
        jack.connect(jack_name+":"+port_name+"_1", "system:playback_1")
        jack.connect(jack_name+":"+port_name+"_2", "system:playback_2")

        port_name = "in"
        jack.register_port(port_name+"_1", jack.IsInput | jack.CanMonitor)
        jack.register_port(port_name+"_2", jack.IsInput | jack.CanMonitor)
        jack.connect("system:capture_1", jack_name+":"+port_name+"_1")
        jack.connect("system:capture_2", jack_name+":"+port_name+"_2")

        self.buffer_size = jack.get_buffer_size()
        self.sample_rate = jack.get_sample_rate()
        self.period = self.buffer_size*0.75/self.sample_rate

        self.blank_data = numpy.zeros((2, self.buffer_size), dtype=numpy.float).astype('f')
        self.empty_data = numpy.zeros((2, self.buffer_size), dtype=numpy.float).astype('f')

        self.record_amplitude = 0

    def get_new_audio_queue(self):
        queue = Queue.Queue()
        self.audio_queues.append(queue)
        return queue

    def remove_audio_queue(self, queue):
        if queue in self.audio_queues:
            self.audio_queues.remove(queue)

    def clear_audio_queue(self, queue):
        try:
            while(queue.get(block=False) is not None):
                pass
        except Queue.Empty as e:
            pass

    def clear_all_audio_queues(self):
        for queue in self.audio_queues:
            self.clear_audio_queue(queue)

    def set_record_file(self, filename):
        self.wave_file = WaveFileWriter(filename=filename, fileob=None, sample_rate=self.sample_rate)

    def save_record_file_as(self, filename):
        src_obj = self.wave_file.get_fileobject()
        if not src_obj:
            return False
        try:
            dest_obj = open(filename, "wb")
        except:
            return False
        self.record_lock.acquire()
        src_obj.seek(0)
        shutil.copyfileobj(src_obj, dest_obj)
        dest_obj.close()
        self.record_lock.release()
        return True

    def create_temp_record_file(self):
        self.record_lock.acquire()
        if self.wave_file:
            self.wave_file.close()
        fileob = tempfile.TemporaryFile(mode="w+b")
        self.wave_file = WaveFileWriter(filename=None, fileob=fileob, sample_rate=self.sample_rate)
        self.record_lock.release()

    def get_buffer_times(self):
        return numpy.arange(self.buffer_size)*1.0/self.sample_rate

    def run(self):
        while not self.should_stop:
            output = None
            for audio_queue in self.audio_queues:
                try:
                    queue_output = audio_queue.get(block=False)
                except Queue.Empty as e:
                    queue_output = None
                if queue_output is None:
                    continue
                if output is None:
                    output = queue_output
                else:
                    span_diff = output.shape[1]-queue_output.shape[1]
                    if span_diff<0:
                        zeros = numpy.zeros((output.shape[0], -span_diff), dtype="f")
                        output = numpy.concatenate((output, zeros), axis=1)
                    elif span_diff>0:
                        zeros = numpy.zeros((output.shape[0], span_diff), dtype="f")
                        queue_output = numpy.concatenate((queue_output, zeros), axis=1)
                    output += queue_output
                queue_output = None

            if output is None:
                output = self.blank_data
            i = 0
            delay = 0
            while i<=output.shape[1]-self.buffer_size:
                st = time.time()
                try:
                    output_data = output[:, i:i+self.buffer_size]
                    if self.record and self.wave_file:
                        input_data = numpy.zeros((2, self.buffer_size), dtype=numpy.float).astype('f')
                    else:
                        input_data = self.empty_data
                    jack.process(output_data, input_data)
                    if self.record and self.wave_file:
                        self.record_lock.acquire()
                        self.wave_file.write(input_data)
                        self.record_lock.release()
                        self.record_amplitude = numpy.amax(input_data)
                    i += self.buffer_size
                except jack.InputSyncError:
                    pass
                except jack.OutputSyncError:
                    pass
                delay = self.period-(time.time()-st)
                if delay<=0:
                    delay = self.period
                time.sleep(delay)
            if delay==0:
                time.sleep(self.period)
        jack.detach()
        self.record_lock.acquire()
        if self.wave_file:
            self.wave_file.close()
        self.wave_file = None
        self.record_lock.release()
        AudioJack._running_thread = None

    def close(self):
        self.should_stop = True
        if self.is_alive():
            self.join()
