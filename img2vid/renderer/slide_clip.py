import numpy
import PIL.Image
import moviepy.editor

from ..effects import Effect
from ..utils import ImageUtils
from .slide_renderer import SlideRenderer
from ..slides import TextSlide, ImageSlide, VideoSlide
from ..effects import MoviePyEffect, NumberParamChange


class SlideClip(moviepy.editor.VideoClip):
    def __init__(self, slide, app_config, size,
                       duration=None, start=None, end=None,
                       *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = size
        self.start = start
        self.duration = duration
        self.end = end
        if end is None and start is not  None and \
           duration is not None:
            self.end = start + duration
        self.make_frame = self._make_frame

        self.slide = slide.clone()
        self.sub_clips = []
        '''
        self.slide.add_effect(MoviePyEffect, {
            'effect_type': 'rotate',
            'effect_params': {"angle": 30, "expand": False}
        }, 'rotation_effect')
        self.slide.add_effect(NumberParamChange, {
            'param_name': 'effects.rotation_effect.effect_params.angle',
            'value_start': 0,
            'value_end': 360,
            'scale': 3
        })
        '''

        self.app_config = app_config

        self._cached_image = None
        self._progress = 0

    def add_sub_clip(self, clip):
        self.sub_clips.append(clip)

    def apply_effects(self, image, time_pos, progress):
        if not self.slide.effects:
            return image
        for effect in self.slide.effects.values():
            eff_delay = effect.delay or 0
            eff_duration = effect.duration or (self.duration - eff_delay)
            if time_pos < eff_delay:
                continue
            if time_pos > eff_delay + eff_duration:
                continue

            # print(effect.TYPE_NAME, effect.APPLY_ON & Effect.APPLY_TYPE_TEXT)
            if self.slide.TYPE_NAME == TextSlide.TYPE_NAME and \
               (effect.APPLY_ON & Effect.APPLY_TYPE_TEXT) == 0:
                continue
            if self.slide.TYPE_NAME == ImageSlide.TYPE_NAME and \
               (effect.APPLY_ON & Effect.APPLY_TYPE_IMAGE) == 0:
                continue
            if self.slide.TYPE_NAME == VideoSlide.TYPE_NAME and \
               (effect.APPLY_ON & Effect.APPLY_TYPE_VIDEO) == 0:
                continue

            self._cached_image = None
            image = effect.transform(
                image=image,
                slide=self.slide,
                clip_time_pos=time_pos,
                clip_progress=progress,
                time_pos=time_pos-eff_delay,
                progress=(time_pos-eff_delay)/eff_duration,
                clip=self
            )
        return image

    def _make_frame_image(self, time_pos, rgba=False):
        if self.duration is None:
            progress = 1
        else:
            progress = (time_pos - self.start)/self.duration
        self.apply_effects(None, time_pos, progress)

        image = self._cached_image
        if not image:
            image = self.get_image_at(time_pos, progress)

        if self.sub_clips:
            for sub_clip in self.sub_clips:
                if time_pos < sub_clip.start:
                    continue
                if time_pos > sub_clip.end:
                    continue
                image = ImageUtils.merge_image(
                    image, sub_clip._make_frame_image(time_pos - sub_clip.start, rgba=True)
                )

        if self.slide.opacity != 1:
            image = ImageUtils.set_alpha(image, self.slide.opacity)

        self._cached_image = image
        return image

    def _make_frame(self, time_pos):
        # print("time_pos", time_pos, self.slide.TYPE_NAME, self.start, self.end)
        image = self._make_frame_image(time_pos)
        bg_image = ImageUtils.create_blank(
            self.app_config.video_render.scaled_width,
            self.app_config.video_render.scaled_height,
            self.app_config.video_render.back_color
        )

        if not self.ismask:
            image = ImageUtils.merge_image(bg_image, image)
        frame = numpy.array(image, dtype=numpy.uint8)
        if self.ismask:
            frame = 1.0 * frame[:, :, 0] / 255
        else:
            frame = frame[:, :, :3]
        return frame
