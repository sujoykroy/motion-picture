from .effect import Effect
from .effect_param import EffectParam

class FadeOut(Effect):
    TYPE_NAME = "fade_out"
    KEY_DURATION = "dur"

    PARAMS = {'duration': EffectParam(float, 2)}

    def __init__(self, duration):
        super().__init__()
        self.duration = duration

    def get_value_at(self, frac):
        return 1-frac

    def get_json(self):
        """Returns json representation."""
        data = super().get_json()
        data[self.KEY_DURATION] = self.duration
        return data

    @classmethod
    def create_from_json(cls, data):
        if data.get(cls.KEY_TYPE, None) != cls.TYPE_NAME:
            return None
        duration = float(data.get(cls.KEY_DURATION))
        newob = cls(duration=duration)
        return newob
