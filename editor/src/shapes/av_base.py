from ..audio_tools import AudioBlock, AudioFileBlock
from ..commons import draw_utils
import numpy

class AVBase(object):
    DONT_PLAY_AUDIO = True

    def __init__(self):
        self.av_filename = None
        self.time_pos = 0.
        self.audio_active = True
        self.duration = 0

    def set_av_filename(self, av_filename):
        if av_filename != self.av_filename:
            self.last_played_at = 0
        self.av_filename = av_filename

    def get_duration(self):
        return self.duration

    def get_av_filename(self):
        return self.av_filename

    def set_time_pos(self, time_pos, prop_data):
        self.time_pos = time_pos

    def draw_for_time_slice(self, ctx, filename, visible_time_span,
                                  time_slice, time_slice_box, pixel_per_second):
        audio_block = AudioFileBlock.get_for_filename(filename)
        if not isinstance(audio_block.samples, numpy.ndarray):
            return
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
            sample = audio_block.samples[int(t*AudioBlock.SampleRate),:]
            if sample is None:
                break
            if not wave_started:
                wave_started = True
                ctx.move_to(t, .5-sample[0]/2)
            else:
                ctx.line_to(t, .5-sample[0]/2)
            t += t_step
        ctx.restore()
        draw_utils.draw_stroke(ctx, 1, "000000")

