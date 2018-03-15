import numpy
import PIL.Image

from .effect import Effect
from .effect_param import EffectParam

class RgbFilter(Effect):
    TYPE_NAME = "rgb_filter"
    APPLY_ON = Effect.APPLY_TYPE_IMAGE
    PARAMS = [
        EffectParam('channel', 'str', 'Red', choices=('Red', 'Green', 'Blue'))
    ]

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    def transform(self, image, progress, **kwargs):
        if self.channel == 'Red':
            one_index = [0]
            zero_indices = [1, 2]
        elif self.channel == 'Green':
            one_index = [1]
            zero_indices = [0, 2]
        elif self.channel == 'Blue':
            one_index = [2]
            zero_indices = [0, 1]
        img_buff = numpy.array(image)
        img_buff[:, :, zero_indices[0]] = img_buff[:, :, zero_indices[0]]*(1-progress)
        img_buff[:, :, zero_indices[1]] = img_buff[:, :, zero_indices[1]]*(1-progress)
        img_buff = img_buff.astype(numpy.uint8)
        return PIL.Image.fromarray(img_buff)
