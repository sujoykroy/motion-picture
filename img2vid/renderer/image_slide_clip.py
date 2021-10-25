from copy import copy

import numpy
import moviepy.editor

from ..utils import ImageUtils
from .caption_renderer import CaptionRenderer
from .slide_renderer import SlideRenderer
from ..slides import TextSlide, ImageSlide, VideoSlide
from .slide_clip import SlideClip


class ImageSlideClip(SlideClip):
    def _make_frame_image(self, time_pos, **kwargs):
        if self.slide.TYPE_NAME == VideoSlide.TYPE_NAME:
            self.slide.current_pos= time_pos

        return super()._make_frame_image(time_pos, **kwargs)

    def get_image_at(self, time_pos, progress):
        render_info = SlideRenderer.build_image_slide_only_image(
            self.slide,
            self.app_config.video_render,
            self.app_config.text
        )

        image = self.apply_effects(render_info.image, time_pos, progress)

        # if render_info.image.width != image.width:
        #    image = ImageUtils.fit_full(
        #            image, render_info.image.width, render_info.image.height)

        if self.slide.caps:
            image = SlideRenderer.build_image_slide_only_captions(
                self.slide,
                self.app_config.video_render,
                self.app_config.text,
                image
        )

        return image
