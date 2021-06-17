import subprocess
import tempfile


import PIL
import PIL.Image
import PIL.ImageDraw

from ..analysers import TextAnalyser
from ..utils import ImageUtils
from ..geom.rectangle import Rectangle
from ..geom.circle import Circle


class VectorRenderer:
    @classmethod
    def create_image(cls, vector_shape, vector_config, wand_image=False, canvas=None):
        if not canvas:
            canvas = ImageUtils.create_blank(vector_shape.width, vector_shape.height, "#FFFFFF00")
        draw = PIL.ImageDraw.Draw(canvas)
        if isinstance(vector_shape, Rectangle):
            draw.rectangle(
                vector_shape.to_array(),
                fill=vector_config.fill_color,
                outline=vector_config.border_color,
                width=vector_config.stroke_width
            )
        elif isinstance(vector_shape, Circle):
            draw.ellipse(
                vector_shape.to_array(),
                fill=vector_config.fill_color,
                outline=vector_config.border_color,
                width=vector_config.stroke_width
            )
        if wand_image:
            canvas = ImageUtils.pil2wand(canvas)
        return canvas
