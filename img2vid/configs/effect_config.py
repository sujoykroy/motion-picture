class EffectConfig:
    def __init__(self, effect_class, effect_data):
        self._defaults = {}
        self._effect_class = effect_class
        for effect_param in effect_class.PARAMS:
            key = effect_param.name
            if key in effect_data:
                value = param.parse(effect_data[key])
            else:
                value = effect_param.default
            self._defaults[key] = value

    @property
    def defaults(self):
        return dict(self._defaults)

    @property
    def effect_class(self):
        return self._effect_class

    @property
    def effect_name(self):
        return self._effect_class.TYPE_NAME
