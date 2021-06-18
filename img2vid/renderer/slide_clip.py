import numpy
import moviepy.editor

from ..effects import Effect
from ..utils import ImageUtils
from .slide_renderer import SlideRenderer
from ..slides import TextSlide, ImageSlide, VideoSlide
from ..effects import MoviePyEffect, NumberParamChange


class SlideClip(moviepy.editor.VideoClip):
    def __init__(self, slide, app_config, size, duration=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = size
        self.duration = duration

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
                image=image, progress=progress,
                slide=self.slide, rel_time=time_pos,
                clip=self
            )
        return image

    def _make_frame_image(self, time_pos, rgba=False):
        if self.duration is None:
            progress = 1
        else:
            progress = time_pos/self.duration
        self.apply_effects(None, time_pos, progress)

        image = self._cached_image
        if not image:
            image = self.get_image_at(time_pos, progress)

        if self.sub_clips:
            for sub_clip in self.sub_clips:
                image = ImageUtils.merge_image(
                    image, sub_clip._make_frame_image(time_pos, rgba=True)
                )

        self._cached_image = image
        return image

    def _make_frame(self, time_pos):
        # print("time_pos", time_pos, self.slide.TYPE_NAME)
        image = self._make_frame_image(time_pos)
        bg_image = ImageUtils.create_blank(
            self.app_config.video_render.scaled_width,
            self.app_config.video_render.scaled_height,
            self.app_config.video_render.back_color
        )
        image = ImageUtils.merge_image(
            bg_image, image
        )
        frame = numpy.array(image, dtype=numpy.uint8)
        if self.ismask:
            frame = 1.0 * frame[:, :, 0] / 255
        else:
            frame = frame[:, :, :3]
        return frame
