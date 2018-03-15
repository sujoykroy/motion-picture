from .effect import Effect
from .effect_param import EffectParam

class FadeIn(Effect):
    TYPE_NAME = "fade_in"

    PARAMS = [EffectParam('duration', 'float', 2, unit='sec')]

    def __init__(self, duration):
        super().__init__()
        self.duration = duration

    def get_value_at(self, frac):
        return frac
