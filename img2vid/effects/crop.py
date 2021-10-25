import math

import moviepy.editor as mve
import PIL.Image
import numpy

from .effect import Effect
from ..geom.rectangle import Rectangle
from ..geom.point import Point
from .effect_param import EffectParam
from ..utils.value_parser import ValueParser
from ..utils import ImageUtils


class CropEffect(Effect):
    TYPE_NAME = "crop"
    APPLY_ON = Effect.APPLY_TYPE_IMAGE | Effect.APPLY_TYPE_VIDEO

    PARAMS = Effect.PARAMS + [
        EffectParam('zoom', 'float', 1),
        EffectParam('offset', 'float', 0)
    ]

    def __init__(self, zoom, offset, **kwargs):
        super().__init__(**kwargs)
        self.zoom = float(zoom)
        self.offset = float(offset)

        self.slide_width = None
        self.slide_height = None

    def transform(self, image, progress, slide, clip, **kwargs):
        if image:
            return image

        if self.slide_width is None:
            if slide.TYPE_NAME == 'video':
                file_image = ImageUtils.fetch_video_frame(
                    filepath=slide.filepath,
                    time_pos=0,
                    crop=None, wand_image=False)
            else:
                file_image = ImageUtils.fetch_image(
                    filepath=slide.local_filepath,
                    crop=None, wand_image=False)

            self.slide_width = file_image.width
            self.slide_height = file_image.height

        clip_aspect_ratio = clip.size[0] / clip.size[1]
        slide_aspect_ratio = self.slide_width/ self.slide_height

        rect = Rectangle(0, 0, 1, 1)
        if clip_aspect_ratio > slide_aspect_ratio:
            rect.set_cxy_wh(
                0.5 * self.slide_width,
                0.5 * self.slide_height,
                self.slide_width/self.zoom,
                self.slide_width/(self.zoom*clip_aspect_ratio)
            )
        else:
            rect.set_cxy_wh(
                0.5 * self.slide_width,
                0.5 * self.slide_height,
                self.slide_height * clip_aspect_ratio/self.zoom,
                self.slide_height/self.zoom
            )

        if clip_aspect_ratio > slide_aspect_ratio:
            rect.translate(Point(0, self.offset*0.5*(self.slide_height-rect.get_height())))
        else:
            rect.translate(Point(self.offset*0.5*(self.slide_width-rect.get_width()), 0))
        slide.rect = rect
        return image
