from .effect import Effect
from .effect_param import EffectParam

class FadeIn(Effect):
    TYPE_NAME = "fade_in"

    PARAMS = Effect.PARAMS +  [
        EffectParam('duration', 'float', 2, unit='sec')]

    def __init__(self, duration, **kwargs):
        super().__init__(**kwargs)
        self.duration = duration

    def get_value_at(self, frac):
        return frac
