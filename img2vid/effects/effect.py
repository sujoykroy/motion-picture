"""Base Effect holder"""

class Effect:
    """This is base abstract class for Effect"""
    TYPE_NAME = None
    KEY_TYPE = "type"

    APPLY_TYPE_IMAGE = "image"
    APPLY_TYPE_VIDEO = "video"
    APPLY_TYPE_TEXT = "text"

    _IdSeed = 0

    PARAMS = []
    APPLY_ON = None

    def __init__(self):
        self._id_num = Effect._IdSeed
        Effect._IdSeed += 1

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

    def transform(self, **kwargs):
        pass

    def get_json(self):
        data = {}
        data[self.KEY_TYPE] = self.TYPE_NAME
        for param in self.PARAMS:
            key = param.name
            data[key] = getattr(self, key)
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
        return cls(**arg_dict)

    @classmethod
    def create_from_json(cls, data):
        kwargs = {}
        for param in cls.PARAMS:
            key = param.name
            kwargs[key] = param.parse(data.get(key, param.default))
        newob = cls(**kwargs)
        return newob
