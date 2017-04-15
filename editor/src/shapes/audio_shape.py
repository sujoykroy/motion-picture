from ..commons import *
from ..audio_tools import *
from text_shape import *
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
        self.AUDIO_ICON = None

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
    AUDIO_ICON = None
    DONT_PLAY = True

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius,
                       x_align=X_ALIGN_CENTER, y_align=Y_ALIGN_MIDDLE, text="Sample",
                       font="10", font_color=None, line_align = 1):
        TextShape.__init__(self, anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius,
                                x_align, y_align, text, font, font_color, line_align)
        self.audio_path = None
        self.time_pos = 0.
        self.audio_queue = None

    def copy(self, copy_name=False, deep_copy=False):
        newob = AudioShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        newob.audio_path = self.audio_path
        self.copy_into(newob, copy_name)
        return newob

    def get_xml_element(self):
        elm = TextShape.get_xml_element(self)
        elm.attrib["audio_path"] = self.audio_path
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(AudioShape, cls).create_from_xml_element(elm)
        shape.set_audio_path(elm.attrib.get("audio_path", ""))
        print "shape.audio_path", shape.audio_path
        return shape

    def set_audio_path(self, audio_path):
        self.audio_path = audio_path

    def set_av_filename(self, filename):
        self.set_audio_path(filename)

    def get_av_filename(self):
        return self.audio_path

    def can_draw_time_slice_for(self, prop_name):
        return True if prop_name == "time_pos" else False

    def get_duration(self):
        audio_file = AudioFileCache.get_file(self.audio_path)
        return audio_file.duration

    def get_sample(self, at):
        audio_file = AudioFileCache.get_file(self.audio_path)
        return audio_file.get_sample_at(at)

    def set_prop_value(self, prop_name, prop_value, prop_data=None):
        if prop_name == "time_pos":
            self.set_time_pos(prop_value, prop_data)
        else:
            super(AudioShape, self).set_prop_value(prop_name, prop_value, prop_data)

    def set_time_pos(self, time_pos, prop_data=None):
        if prop_data:
            self.set_av_filename(prop_data["av_filename"])
        self.time_pos = time_pos
        if AudioShape.DONT_PLAY:
            return
        if self.audio_queue is None:
            self.audio_queue = Queue.Queue(1)
            if AudioShape.AUDIO_PROCESS_THREAD is None:
                AudioShape.AUDIO_PROCESS_THREAD = AudioProcessThread()
            AudioShape.AUDIO_PROCESS_THREAD.attach_audio_shape(self)

        audio_file = AudioFileCache.get_file(self.audio_path)
        start_at = self.time_pos
        end_at = self.time_pos + self.TIME_STEP
        samples = audio_file.get_samples_in_between(start_at, end_at)
        try:
            self.audio_queue.put(samples, block=False)
        except Queue.Full as e:
            pass

    def draw_image(self, ctx):
        if self.AUDIO_ICON is None:
            return
        ctx.save()
        ctx.translate(0, -self.AUDIO_ICON.get_abs_outline(0).height*1.2)
        self.AUDIO_ICON.draw(ctx)
        ctx.restore()

    def draw_for_time_slice(self, ctx, prop_name, prop_data, visible_time_span,
                                 time_slice, time_slice_box, pixel_per_second):
        if prop_name != "time_pos":
            return
        filename = prop_data["av_filename"]
        if not filename:
            filename = self.audio_path
        wave_file = AudioFileCache.get_file(filename)

        diff_value = abs(time_slice.end_value - time_slice.start_value)
        if diff_value ==0:
            diff_value = 0.001
        slice_scale = time_slice.duration/diff_value

        time_start = time_slice.start_value + visible_time_span.start/slice_scale
        time_end = min(time_slice.end_value, (time_slice.start_value+visible_time_span.end/slice_scale))
        t_step = 1./(slice_scale*visible_time_span.scale*pixel_per_second)
        t = time_start

        ctx.save()
        time_slice_box.pre_draw(ctx)
        ctx.scale(pixel_per_second, time_slice_box.height)
        ctx.scale(slice_scale, 1)
        ctx.translate(-time_slice.start_value, 0)

        wave_started = False
        while t<time_end:
            sample = wave_file.get_sample_at(t)
            if sample is None:
                break
            if not wave_started:
                wave_started = True
                ctx.move_to(t, .5-sample[0]/2)
            else:
                ctx.line_to(t, .5-sample[0]/2)
            t += t_step

        ctx.restore()
        draw_stroke(ctx, 1, "000000")

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

