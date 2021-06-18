import math

import moviepy.editor as mve
import PIL.Image
import numpy

from .effect import Effect
from .effect_param import EffectParam
from ..utils.value_parser import ValueParser

class NumberParamChange(Effect):
    TYPE_NAME = "number_param_change"
    APPLY_ON = Effect.APPLY_TYPE_ALL

    CHANGE_TYPE_LINEAR = 'linear'

    PARAMS = Effect.PARAMS + [
        EffectParam('param_name', 'str', None),
        EffectParam('value_start', 'float', None),
        EffectParam('value_end', 'float', None),
        EffectParam('change_type', 'str', CHANGE_TYPE_LINEAR, choices=[CHANGE_TYPE_LINEAR]),
        EffectParam('scale', 'int', 1),
    ]

    def __init__(self, param_name, value_start, value_end, change_type, scale=1, **kwargs):
        super().__init__(**kwargs)
        self.param_name = param_name
        self._param_paths = param_name.split(".")
        self.value_start = float(value_start)
        self.value_end = float(value_end)
        self.change_type = change_type
        self.scale = int(scale)

    def get_name(self):
        return "{0}_{1}".format(self.TYPE_NAME, self.param_name)

    def transform(self, image, progress, slide, clip, **kwargs):
        if image:
            return image
        obj = ValueParser.find_in_paths(slide, self._param_paths[:-1])
        value = ValueParser.find_in_paths(obj, self._param_paths[-1:])
        if value is None:
            return image
        frac = (min(1, max(0, progress * self.scale)))

        if self.change_type == self.CHANGE_TYPE_LINEAR:
            value = self.value_start + (self.value_end - self.value_start) * frac
        # print(self._param_paths, value, progress, self.scale)
        if isinstance(obj, dict) or isinstance(obj, list):
            obj[self._param_paths[-1]] = value
        else:
            setattr(obj, self._param_paths[-1], value)
        return image
