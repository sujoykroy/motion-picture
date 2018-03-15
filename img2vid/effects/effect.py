"""Base Effect holder"""

class Effect:
    """This is base abstract class for Effect"""
    TYPE_NAME = None
    KEY_TYPE = "type"

    APPLY_TYPE_IMAGE = "image"
    APPLY_TYPE_VIDEO = "video"
    APPLY_TYPE_TEXT = "text"

    _IdSeed = 0

    PARAMS = {}
    APPLY_ON = None

    def __init__(self):
        self._id_num = Effect._IdSeed
        Effect._IdSeed += 1

    def __hash__(self):
        return hash("Effect{}".format(self._id_num))

    def get_json(self):
        """Returns json representation."""
        data = {}
        data[self.KEY_TYPE] = self.TYPE_NAME
        return data

    @classmethod
    def create_from_values(cls, value_data):
        arg_dict = {}
        for key, param in cls.PARAMS.items():
            if key in value_data:
                value = value_data[key]
                value = param.parse(value)
            else:
                value = param.default_value
            arg_dict[key] = value
        return cls(**arg_dict)

    def update_from_values(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.PARAMS:
                param = self.PARAMS[key]
                value = param.parse(value)
                if hasattr(self, param):
                    setattr(self, param, value)
