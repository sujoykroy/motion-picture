from copy import copy

import numpy
import moviepy.editor

from ..utils import ImageUtils
from .slide_renderer import SlideRenderer
from ..slides.geom_slide import GeomSlide
from .slide_clip import SlideClip


class GeomSlideClip(SlideClip):
    def get_image_at(self, time_pos, progress):
        render_info = SlideRenderer.build_geom_slide(
            self.slide,
            self.app_config.video_render,
            "#000000"
        )

        image = self.apply_effects(render_info.image, time_pos, progress)

        return image
