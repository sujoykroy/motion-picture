import jack
import threading, Queue, time, wave, numpy, math

class JackTask(threading.Thread):
    def __init__(self, audioQueue):
        threading.Thread.__init__(self)
        self.shouldStop = False
        self.audioQueue = audioQueue
        try:
            jack.attach("seq")
        except jack.NotConnectedError as e:
            self.shouldStop = True
            return
        jack.register_port("out_1", jack.IsOutput | jack.CanMonitor)
        jack.register_port("out_2", jack.IsOutput | jack.CanMonitor)
        jack.activate()
        jack.connect("seq:out_1", "system:playback_1")
        jack.connect("seq:out_2", "system:playback_2")
        self.bufferSize = jack.get_buffer_size()
        self.sampleRate = jack.get_sample_rate()
        self.period = self.bufferSize*0.75/self.sampleRate

        self.emptyData = numpy.zeros((2,5), dtype=numpy.float).astype('f')
        self.blankData = numpy.zeros((2,self.bufferSize), dtype=numpy.float).astype('f')

    def run(self):
        while not self.shouldStop:
            if self.audioQueue.qsize()<1:
                startTime = time.time()
                try:
                    jack.process(self.blankData, self.emptyData)
                except jack.InputSyncError:
                    pass
                except jack.OutputSyncError:
                    pass
                elapsedTime = time.time() - startTime
                diffTime = self.period - elapsedTime
                if diffTime>0:
                    time.sleep(diffTime)
                continue
            try:
                output = self.audioQueue.get(block=False)
            except Queue.Empty as e:
                continue
            i = 0
            while i<=output.shape[1]-self.bufferSize:
                startTime = time.time()
                try:
                    jack.process(output[:, i:i+self.bufferSize], self.emptyData)
                    i += self.bufferSize
                except jack.InputSyncError:
                    pass
                except jack.OutputSyncError:
                    #print "sync error"
                    pass
                elapsedTime = time.time() - startTime
                diffTime = self.period - elapsedTime
                if diffTime>0:
                    time.sleep(diffTime)
        jack.detach()


