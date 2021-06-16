import json

class EffectParam:
    def __init__(self,
                 name, type_class, default, **kwargs):
        self._name = name
        self._type_class = type_class
        self._default = default
        if not kwargs:
            options = {}
        else:
            options = dict(kwargs)
        self._options = options

    def parse(self, value):
        if self._type_class == 'int':
            return int(value)
        elif self._type_class == 'float':
            return float(value)
        elif self._type_class == 'json':
            if isinstance(value, str):
                return json.loads(value)
        return value

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default

    @property
    def type_class(self):
        return self._type_class

    @property
    def choices(self):
        return self._options.get('choices', [])

    @property
    def range(self):
        return self._options.get('range', None)
