from ..commons import *
from ..audio_tools import *
from text_shape import *
import sys, os
import time, Queue

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
        self.audio_active = True

    @classmethod
    def build_time_step(self, mult):
        AudioShape.TIME_STEP = .1*mult

    def copy(self, copy_name=False, deep_copy=False):
        newob = AudioShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        newob.audio_path = self.audio_path
        self.copy_into(newob, copy_name)
        return newob

    def get_xml_element(self):
        elm = TextShape.get_xml_element(self)
        elm.attrib["audio_path"] = self.audio_path
        if not self.audio_active:
            elm.attrib["audio_active"] = "0"
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(AudioShape, cls).create_from_xml_element(elm)
        shape.set_audio_path(elm.attrib.get("audio_path", ""))
        shape.audio_active = bool(int(elm.attrib.get("audio_active", 1)))
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

    def get_audio_length(self):
        return "{0:.2f} sec".format(self.get_duration())

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
        if AudioShape.DONT_PLAY or not self.audio_path:
            return

        audio_jack = AudioJack.get_thread()
        if not audio_jack:
            return
        if self.audio_queue is None:
            self.audio_queue = audio_jack.get_new_audio_queue()

        audio_file = AudioFileCache.get_file(self.audio_path)
        start_at = self.time_pos
        end_at = self.time_pos + self.TIME_STEP
        samples = audio_file.get_samples_in_between(start_at, end_at).copy()
        AudioJack.get_thread().clear_audio_queue(self.audio_queue)
        try:
            self.audio_queue.put(samples, block=False)
        except Queue.Full as e:
            pass

    def draw_image(self, ctx, root_shape=None):
        if self.AUDIO_ICON is None:
            return
        ctx.save()
        ctx.translate(0, -self.AUDIO_ICON.get_abs_outline(0).height*1.2)
        self.AUDIO_ICON.draw(ctx)
        ctx.restore()

    @staticmethod
    def draw_for_time_slice(ctx, prop_name, prop_data, visible_time_span,
                                 time_slice, time_slice_box, pixel_per_second):
        if prop_name != "time_pos":
            return
        filename = prop_data["av_filename"] if prop_data else None
        if not filename:
            return
        wave_file = AudioFileCache.get_file(filename)
        diff_value = abs(time_slice.end_value - time_slice.start_value)
        if diff_value ==0:
            diff_value = 0.001
        slice_scale = time_slice.duration/diff_value

        time_start = time_slice.start_value + visible_time_span.start/slice_scale
        time_end = min(time_slice.end_value, (time_slice.start_value+visible_time_span.end/slice_scale))
        t_step = 1./(slice_scale*visible_time_span.scale*pixel_per_second)
        t_step = max((time_end-time_start)/1000., t_step)

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
        if self.audio_queue:
            audio_jack = AudioJack.get_thread()
            if audio_jack:
                audio_jack.remove_audio_queue(self.audio_queue)
        self.audio_queue = None
