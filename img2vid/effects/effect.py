"""Base Effect holder"""
from .effect_param import EffectParam

class Effect:
    """This is base abstract class for Effect"""
    TYPE_NAME = None
    KEY_TYPE = "type"
    KEY_DELAY = "delay"
    KEY_DURATION = "duration"


    THROTTLE_KEYS = [KEY_DURATION, KEY_DELAY]

    APPLY_TYPE_IMAGE = 1
    APPLY_TYPE_VIDEO = 3
    APPLY_TYPE_TEXT = 4

    APPLY_TYPE_ALL = APPLY_TYPE_IMAGE | APPLY_TYPE_VIDEO | APPLY_TYPE_TEXT

    _IdSeed = 0

    PARAMS = [
        EffectParam(KEY_DELAY, 'float', None),
        EffectParam(KEY_DURATION, 'float', None)
    ]
    APPLY_ON = 0

    def __init__(self, sort_weight=0, delay=None, duration=None):
        self._id_num = Effect._IdSeed
        self.sort_weight = sort_weight
        self.delay = delay
        self.duration = duration
        Effect._IdSeed += 1

    def get_delay(self):
        return self.delay or 0

    def get_duration(self, default_dur):
        return self.duration or default_dur

    def get_name(self):
        return self.TYPE_NAME

    def __hash__(self):
        return hash("Effect{}".format(self._id_num))

    def set_param(self, param_name, value):
        if hasattr(self, param_name):
            setattr(self, param_name, value)

    def get_param(self, param_name):
        if hasattr(self, param_name):
            return getattr(self, param_name)
        raise AttributeError

    def update_from_values(self, **kwargs):
        for param in self.PARAMS:
            key = param.name
            if key in kwargs:
                value = param.parse(kwargs[key])
                self.set_param(key, value)

    def transform(self, image, **kwargs):
        return image

    def get_json(self):
        data = {'sort_weight': self.sort_weight}
        data[self.KEY_TYPE] = self.TYPE_NAME
        for param in self.PARAMS:
            key = param.name
            data[key] = getattr(self, key)
        for key in self.THROTTLE_KEYS:
            if data[key] is None:
                del data[key]
        return data

    @classmethod
    def create_from_values(cls, value_data):
        arg_dict = {}
        for param in cls.PARAMS:
            key = param.name
            if key in value_data:
                value = value_data[key]
                value = param.parse(value)
            else:
                value = param.default
            arg_dict[key] = value
        arg_dict['sort_weight'] = value_data.get('sort_weight', 0)
        return cls(**arg_dict)

    @classmethod
    def create_from_json(cls, data):
        kwargs = {}
        for param in cls.PARAMS:
            key = param.name
            kwargs[key] = param.parse(data.get(key, param.default))
        kwargs['sort_weight'] = data.get('sort_weight', 0)
        newob = cls(**kwargs)
        return newob
