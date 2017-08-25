from ..commons import *
from ..audio_tools import AudioFileBlock, AudioBlock
from av_base import AVBase
from text_shape import *
import sys, os
import time, Queue

class AudioShape(TextShape, AVBase):
    TYPE_NAME = "Audio"
    AUDIO_ICON = None
    DONT_PLAY = True

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius,
                       x_align=X_ALIGN_CENTER, y_align=Y_ALIGN_MIDDLE, text="Sample",
                       font="10", font_color=None, line_align = 1):
        TextShape.__init__(self, anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius,
                                x_align, y_align, text, font, font_color, line_align)
        AVBase.__init__(self)

    def copy(self, copy_name=False, deep_copy=False):
        newob = AudioShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        newob.set_av_filename(self.av_filename)
        self.copy_into(newob, copy_name)
        return newob

    def get_xml_element(self):
        elm = super(AudioShape, self).get_xml_element()
        elm.attrib["audio_path"] = self.av_filename
        if not self.audio_active:
            elm.attrib["audio_active"] = "0"
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(AudioShape, cls).create_from_xml_element(elm)
        shape.set_av_filename(elm.attrib.get("audio_path", ""))
        shape.audio_active = bool(int(elm.attrib.get("audio_active", 1)))
        return shape

    def get_duration(self):
        audio_block = AudioFileBlock.get_for_filename(self.av_filename)
        return audio_block.duration*1./AudioBlock.SampleRate

    def get_audio_length(self):
        return "{0:.2f} sec".format(self.get_duration())

    def get_audio_path(self):
        return self.av_filename

    def set_audio_path(self, filename):
        self.set_av_filename(filename)

    def set_prop_value(self, prop_name, prop_value, prop_data=None):
        if prop_name == "time_pos":
            self.set_time_pos(prop_value, prop_data)
        else:
            super(AudioShape, self).set_prop_value(prop_name, prop_value, prop_data)

    def set_time_pos(self, time_pos, prop_data=None):
        if prop_data:
            av_filename = prop_data.get("audio_path")
            self.set_av_filename(av_filename)

        if self.av_filename == "//":
            return
        AVBase.set_time_pos(self, time_pos, prop_data)

    def draw_image(self, ctx, root_shape=None):
        if self.AUDIO_ICON is None:
            return
        ctx.save()
        ctx.translate(0, -self.AUDIO_ICON.get_abs_outline(0).height*1.2)
        self.AUDIO_ICON.draw(ctx)
        ctx.restore()

    def draw(self, ctx, fixed_border=True, root_shape=None):
        super(AudioShape, self).draw(ctx, fixed_border=fixed_border, root_shape=root_shape)
        ctx.save()
        self.AUDIO_ICON.draw(ctx)
        ctx.restore()

    def can_draw_time_slice_for(self, prop_name):
        return True if prop_name == "time_pos" else False

    def draw_for_time_slice(self, ctx, prop_name, prop_data, visible_time_span,
                                   time_slice, time_slice_box, pixel_per_second):
        if prop_name != "time_pos":
            return
        filename = prop_data["audio_path"] if prop_data else None
        if not filename or filename == "//":
            return

        AVBase.draw_for_time_slice(
            self, ctx, filename, visible_time_span,
                       time_slice, time_slice_box, pixel_per_second)
