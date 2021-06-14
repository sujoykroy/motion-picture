import numpy
import moviepy.editor

from ..effects import Effect
from ..utils import ImageUtils
from .slide_renderer import SlideRenderer
from ..slides import TextSlide, ImageSlide, VideoSlide


class SlideClip(moviepy.editor.VideoClip):
    def __init__(self, slide, app_config, size, duration=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = size
        self.duration = duration

        self.make_frame = self._make_frame

        self.slide = slide.clone()
        self.app_config = app_config

        self._cached_image = None
        self._progress = 0

    def apply_effects(self, time_pos, image, progress):
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

    def _make_frame(self, time_pos):
        progress = time_pos/self.duration
        self.apply_effects(None, time_pos, progress)

        image = self._cached_image
        if not image:
            image = self.get_image_at(time_pos)
            self._cached_image = image

        video_config = self.app_config.video_render
        if image.width != self.size[0] or \
           image.height != self.size[1]:
            image = ImageUtils.fit_full(image, self.size[0], self.size[1])

        # image = self.apply_effects(image, time_pos, progress)

        frame = numpy.array(image, dtype=numpy.uint8)
        frame = frame[:, :, :3]
        return frame
