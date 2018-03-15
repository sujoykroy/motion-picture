"""This module provides Effects."""
from .effect import Effect
from .scale_pan import ScalePan

from .fade_in import FadeIn
from .fade_out import FadeOut
from .rgb_filter import RgbFilter

_EFFECT_CLASSES = (FadeIn, FadeOut, RgbFilter)

def create_effect_from_json(data):
    """Parses json data and returns corresponding Effect."""
    if Effect.KEY_TYPE in data:
        filter_type = data[Effect.KEY_TYPE]
        for effect_klass in _EFFECT_CLASSES:
            if filter_type == effect_klass.TYPE_NAME:
                return effect_klass.create_from_json(data)
    return None

EFFECT_TYPES = {}

for flt in _EFFECT_CLASSES:
    EFFECT_TYPES[flt.TYPE_NAME] = flt
