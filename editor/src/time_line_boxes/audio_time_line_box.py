from ..commons.draw_utils import *
from sizes import *
from box import Box
from prop_time_line_box import PropTimeLineBox
import os
from .. import settings

class AudioTimeLineBox(Box):
    def __init__(self, audio_time_line, multi_shape_time_line_box):
        Box.__init__(self, multi_shape_time_line_box)
        self.audio_time_line = audio_time_line
        self.audio_container_box = Box(self)
        self.audio_container_box.left = PropTimeLineBox.TOTAL_LABEL_WIDTH
        self.highlighted = False
        self.update()

    def set_time_multiplier(self, scale):
        self.audio_container_box.scale_x = scale

    def set_vertical_multiplier(self, scale):
        self.audio_container_box.scale_y *= scale

    def update(self):
        self.width = self.audio_time_line.get_duration()*PIXEL_PER_SECOND*self.audio_container_box.scale_x\
                     + self.audio_container_box.left
        self.working_height = HEIGHT_PER_TIME_SLICE
        self.height = self.working_height*self.audio_container_box.scale_y + PROP_TIME_LINE_VERTICAL_PADDING

    def draw(self, ctx, time_start, time_end):
        ctx.save()
        self.pre_draw(ctx)
        ctx.rectangle(0, 0, 2000, self.working_height)
        ctx.restore()
        draw_stroke(ctx, 1, "aaaaaa")

        #draw audio wave
        ctx.save()
        self.audio_container_box.pre_draw(ctx)

        draw_rounded_rectangle(ctx, 0, 0, self.width, self.working_height, 0)
        if self.highlighted:
            draw_fill(ctx, "D6E424")
        else:
            draw_fill(ctx, "eda4b5")
        draw_rounded_rectangle(ctx, 0, 0, self.width, self.working_height, 0)
        #draw_stroke(ctx, 1, "000000")

        t_step = 1./(self.audio_container_box.scale_x*PIXEL_PER_SECOND)
        t = time_start

        ctx.scale(PIXEL_PER_SECOND, self.working_height)
        #ctx.scale(1, -1)
        ctx.translate(-time_start, 0)

        wave_started = False
        while t<time_end:
            sample = self.audio_time_line.get_sample(t)
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

        ctx.save()
        self.pre_draw(ctx)
        ctx.rectangle(-SHAPE_LINE_LEFT_PADDING-2, -5,
                    PropTimeLineBox.TOTAL_LABEL_WIDTH+SHAPE_LINE_LEFT_PADDING, self.height+5)
        ctx.restore()
        draw_fill(ctx, PROP_LEFT_BACK_COLOR)

        draw_text(ctx,
            os.path.basename(self.audio_time_line.filename), 0, 0, font_name=settings.TIME_LINE_FONT,
            width=PROP_NAME_LABEL_WIDTH,
            text_color = PROP_NAME_TEXT_COLOR, padding=PROP_NAME_LABEL_RIGHT_PADDING,
            border_color = PROP_NAME_BORDER_COLOR, border_width=2,
            back_color = PROP_NAME_BACK_COLOR, pre_draw=self.pre_draw)



