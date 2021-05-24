import moviepy.editor as mve
import PIL.Image
import numpy

from .effect import Effect
from .effect_param import EffectParam

class Painted(Effect):
    TYPE_NAME = "painted"
    APPLY_ON = Effect.APPLY_TYPE_VIDEO
    PARAMS = []

    def __init__(self):
        super().__init__()

    def transform(self, image, progress, **kwargs):
        clip = mve.ImageClip(numpy.array(image))
        painting = clip.fx(mve.vfx.painting, saturation = 1.6, black = 0.006)
        return PIL.Image.fromarray(painting.get_frame(0)).convert('RGBA')
