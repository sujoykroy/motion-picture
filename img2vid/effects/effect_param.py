class EffectParam:
    def __init__(self, type_class, default_value):
        self._type_class = type_class
        self._default_value = default_value

    def parse(self, value):
        if self._type_class == int:
            return int(value)
        elif self._type_class == float:
            return float(value)
        return value

    @property
    def default_value(self):
        return self._default_value
