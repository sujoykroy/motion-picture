from copy import copy

import numpy
import moviepy.editor

from ..utils import ImageUtils
from .caption_renderer import CaptionRenderer
from .slide_renderer import SlideRenderer
from ..slides import TextSlide, ImageSlide, VideoSlide
from .slide_clip import SlideClip


class ImageSlideClip(SlideClip):
    def get_image_at(self, time_pos):
        render_info = SlideRenderer.build_image_slide(
            self.slide,
            self.app_config.video_render,
            self.app_config.text
        )
        return render_info.image
