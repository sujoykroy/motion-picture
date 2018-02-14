class EffectConfig:
    def __init__(self, effect_class, effect_data):
        self._defaults = {}
        self._effect_class = effect_class
        for key, param in effect_class.PARAMS.items():
            if key in effect_data:
                value = param.parse(effect_data[key])
                self._defaults[key] = value

    @property
    def defaults(self):
        return dict(self._defaults)

    @property
    def effect_class(self):
        return self._effect_class
