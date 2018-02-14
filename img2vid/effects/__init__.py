"""This module provides Effects."""
from .effect import Effect
from .fade_in import FadeIn
from .fade_out import FadeOut
from .scale_pan import ScalePan

def create_effect_from_json(data):
    """Parses json data and returns corresponding Effect."""
    if Effect.KEY_TYPE in data:
        filter_type = data[Effect.KEY_TYPE]
        if filter_type == FadeIn.TYPE_NAME:
            return FadeIn.create_from_json(data)
        if filter_type == FadeOut.TYPE_NAME:
            return FadeOut.create_from_json(data)
    return None

EFFECT_TYPES = {}

for flt in [FadeIn, FadeOut]:
    EFFECT_TYPES[flt.TYPE_NAME] = flt
