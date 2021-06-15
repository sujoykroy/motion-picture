import subprocess
import tempfile


import PIL
import PIL.Image
import PIL.ImageDraw

from ..analysers import TextAnalyser
from ..utils import ImageUtils
from ..geom.rectangle import Rectangle


class VectorRenderer:
    @classmethod
    def create_image(cls, vector_shape, vector_config, wand_image=False):
        image = ImageUtils.create_blank(vector_shape.width, vector_shape.height, "#FFFFFF00")
        draw = PIL.ImageDraw.Draw(image)
        if isinstance(vector_shape, Rectangle):
            draw.rectangle(
                vector_shape.to_array(),
                fill=vector_config.fill_color,
                outline=vector_config.border_color,
                width=vector_config.stroke_width
            )

        if wand_image:
            image = ImageUtils.pil2wand(image)
        return image
