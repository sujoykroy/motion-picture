from ..commons import *
from text_shape import TextShape, Shape
from moviepy.editor import *
import sys, os
import jack, numpy

import threading, time, Queue

JACK_NAME = "mpa"
class AudioProcessThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.audio_shape_count = 0
        self.audio_shapes = dict()
        self.append_audio_shape_queue = Queue.Queue()
        self.remove_audio_shape_queue = Queue.Queue()

        self.should_stop = False
        self.started = False
        self.period = .1
        try:
            jack.attach(JACK_NAME)
            jack.activate()
        except jack.UsageError as e:
            pass
        except jack.NotConnectedError as e:
            self.should_stop = True
            return

        self.buffer_size = jack.get_buffer_size()
        self.sampleRate = jack.get_sample_rate()
        self.period = self.buffer_size*0.75/self.sampleRate

        self.empty_data = numpy.zeros((2,5), dtype=numpy.float).astype('f')
        self.blank_data = numpy.zeros((2,self.buffer_size), dtype=numpy.float).astype('f')
        self.audio_icon = None

    def attach_audio_shape(self, audio_shape):
        self.append_audio_shape_queue.put(audio_shape)
        if not self.started:
            self.started = True
            self.start()

    def detach_audio_shape(self, audio_shape):
        self.remove_audio_shape_queue.put(audio_shape)

    def run(self):
        while not self.should_stop:
            if not self.append_audio_shape_queue.empty():
                while True:
                    try:
                        audio_shape=self.append_audio_shape_queue.get(block=False)
                    except Queue.Empty as e:
                        break
                    self.audio_shapes[audio_shape] = audio_shape

                if self.audio_shape_count<len(self.audio_shapes):
                    for i in range(self.audio_shape_count, len(self.audio_shapes), 1):
                        port_name = "out_{0}".format(i)
                        jack.register_port(port_name+"_1", jack.IsOutput | jack.CanMonitor)
                        jack.register_port(port_name+"_2", jack.IsOutput | jack.CanMonitor)
                        jack.connect(JACK_NAME+":"+port_name+"_1", "system:playback_1")
                        jack.connect(JACK_NAME+":"+port_name+"_2", "system:playback_2")
                    self.audio_shape_count = len(self.audio_shapes)

            if not self.remove_audio_shape_queue.empty():
                while True:
                    try:
                        audio_shape=self.remove_audio_shape_queue.get(block=False)
                    except Queue.Empty as e:
                        break
                    if audio_shape in self.audio_shapes:
                        del self.audio_shapes[audio_shape]

            if self.audio_shape_count == 0:#probabley this is a never reaching point
                time.sleep(self.period)
                continue

            output = None
            for audio_shape in self.audio_shapes.values():
                if audio_shape.audio_queue is None:
                    continue
                try:
                    audio_shape_output = audio_shape.audio_queue.get(block=False)
                except Queue.Empty as e:
                    continue
                if output is None:
                    output = audio_shape_output
                else:
                    output = numpy.concatenate((output, audio_shape_output), axis=0)

            if output is None:
                for i in range(self.audio_shape_count):
                    if output is None:
                        output = self.blank_data
                    else:
                        output = numpy.concatenate((output, self.blank_data), axis=0)
            else:
                for i in range(output.shape[0]/2, self.audio_shape_count, 1):
                    if self.blank_data.shape[1]<output.shape[1]:
                        extra_blank = numpy.array([[0], [0]]).repeat(
                               output.shape[1]-self.blank_data.shape[1], axis=1).astype('f')
                        print extra_blank.shape
                        self.blank_data = numpy.concatenate((self.blank_data, extra_blank), axis=1)
                    output = numpy.concatenate((output, self.blank_data[:, 0:output.shape[1]]), axis=0)

            i = 0
            while i<=output.shape[1]-self.buffer_size:
                start_time = time.time()
                try:
                    jack.process(output[:, i:i+self.buffer_size], self.empty_data)
                    i += self.buffer_size
                except jack.InputSyncError:
                    pass
                except jack.OutputSyncError:
                    #print "sync error"
                    pass
                elapsed_time = time.time() - start_time
                diff_time = self.period - elapsed_time
                if diff_time>0:
                    time.sleep(diff_time)
        jack.detach()

class AudioShape(TextShape):
    TYPE_NAME = "Audio"
    TIME_STEP = .1
    AUDIO_PROCESS_THREAD = None

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        TextShape.__init__(self, anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        self.audio_path = None
        self.audio_samples = None
        self.duration = 0
        self.time_pos = 0.
        self.audio_queue = None

    def copy(self, copy_name=False, deep_copy=False):
        newob = AudioShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_audio_path(self.audio_path)
        return newob

    def get_xml_element(self):
        elm = AudioShape.get_xml_element(self)
        elm.attrib["audio_path"] = self.audio_path
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        arr.append(float(elm.attrib.get("corner_radius", 0)))
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        shape.set_audio_path(elm.attrib.get("audio_path", ""))
        self._load_samples()
        return shape

    def set_audio_path(self, audio_path):
        self.audio_path = audio_path
        audioclip = AudioFileClip(self.audio_path)
        self.duration = audioclip.duration
        self.set_text(os.path.basename(audio_path))

    def _load_samples(self):
        audioclip = AudioFileClip(self.audio_path)
        buffersize = 1000
        self.audio_samples = audioclip.to_soundarray(buffersize=buffersize)\
                                      .transpose().astype(numpy.float32)
        self.audio_fps = audioclip.fps
        self.duration = audioclip.duration

    def get_sample(self, at):
        if self.audio_samples is None:
            self._load_samples()

        pos = int(at*self.audio_fps)
        if pos<0 or pos>=self.audio_samples.shape[1]:
            return None
        return self.audio_samples[:, pos]

    def set_time_pos(self, time_pos):
        self.time_pos = time_pos
        if self.audio_queue is None:
            self._load_samples()
            self.audio_queue = Queue.Queue(1)
            if AudioShape.AUDIO_PROCESS_THREAD is None:
                AudioShape.AUDIO_PROCESS_THREAD = AudioProcessThread()

            AudioShape.AUDIO_PROCESS_THREAD.attach_audio_shape(self)

        if time_pos<0 or time_pos>self.duration:
            return

        s = int(self.time_pos*self.audio_fps)
        st = time.time()
        samples = self.audio_samples[:, s: s+int(self.TIME_STEP*self.audio_fps)]
        try:
            self.audio_queue.put(samples, block=False)
        except Queue.Full as e:
            pass

    def draw_image(self, ctx):
        if self.audio_icon is None:
            return
        ctx.save()
        ctx.translate(0, -self.audio_icon.get_abs_outline(0).height*1.2)
        self.audio_icon.draw(ctx)
        ctx.restore()

    def cleanup(self):
        TextShape.cleanup(self)
        if AudioShape.AUDIO_PROCESS_THREAD is not None:
            AudioShape.AUDIO_PROCESS_THREAD.detach_audio_shape(self)


    @classmethod
    def cleanup_threads(cls):
        if AudioShape.AUDIO_PROCESS_THREAD is not None:
            AudioShape.AUDIO_PROCESS_THREAD.should_stop = True
            AudioShape.AUDIO_PROCESS_THREAD.join()
            AudioShape.AUDIO_PROCESS_THREAD = None

