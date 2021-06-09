import moviepy.editor as mve
import PIL.Image
import numpy

from .effect import Effect
from .effect_param import EffectParam

class NumberParamChange(Effect):
    TYPE_NAME = "number_param_change"
    APPLY_ON = Effect.APPLY_TYPE_ALL

    CHANGE_TYPE_LINEAR = 'linear'

    PARAMS = [
        EffectParam('param_name', 'str', None),
        EffectParam('value_start', 'float', None),
        EffectParam('value_end', 'float', None),
        EffectParam('change_type', 'str', CHANGE_TYPE_LINEAR, choices=[CHANGE_TYPE_LINEAR]),
    ]

    def __init__(self, param_name, value_start, value_end, change_type):
        super().__init__()
        self.param_name = param_name
        self.value_start = value_start
        self.value_end = value_end
        self.change_type = change_type

    def get_name(self):
        return "{0}_{1}".format(self.TYPE_NAME, self.param_name)


    def transform(self, image, progress, slide, **kwargs):
        if not hasattr(slide, self.param_name):
            return image

        if self.change_type == self.CHANGE_TYPE_LINEAR:
            value = self.value_start + (self.value_end - self.value_start) * progress
        setattr(slide, self.param_name, value)
        return image
