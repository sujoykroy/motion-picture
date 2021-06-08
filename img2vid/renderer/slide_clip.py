from copy import copy

import numpy
import moviepy.editor

from ..utils import ImageUtils
from .slide_renderer import SlideRenderer
from ..slides import TextSlide, ImageSlide, VideoSlide


class SlideClip(moviepy.editor.VideoClip):
    def __init__(self, slide, app_config, size, duration=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = size
        self.duration = duration

        self.make_frame = self._make_frame

        self._orig_slide = slide
        self._modified_slide = copy(slide)
        self.app_config = app_config

        self._cached_image = None
        self._progress = 0

    @property
    def slide(self):
        return self._modified_slide

    def _make_frame(self, time_pos):
        image = self._cached_image
        if not image:
            image = self.get_image_at(time_pos)
            self._cached_image = image

        video_config = self.app_config.video_render
        if image.width != self.size[0] or \
           image.height != self.size[1]:
            image = ImageUtils.fit_full(image, self.size[0], self.size[1])

        frame = numpy.array(image, dtype=numpy.uint8)
        frame = frame[:, :, :3]
        return frame
