from .effect import Effect
from .effect_param import EffectParam

class FadeOut(Effect):
    TYPE_NAME = "fade_out"

    PARAMS = [EffectParam('duration', 'float', 2, unit='sec')]

    def __init__(self, duration, **kwargs):
        super().__init__(**kwargs)
        self.duration = duration

    def get_value_at(self, frac):
        return 1-frac
