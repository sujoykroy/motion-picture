class TextConfig:
    INCH2PIXEL = 72
    TYPE_NAME = 'text_config'

    def __init__(self, **kwargs):
        self.params = dict(kwargs)

    @property
    def scale(self):
        return self.params.get("scale", 1)

    @scale.setter
    def scale(self, value):
        self.params["scale"] = value

    @property
    def font_name(self):
        return self.params.get("font_name")

    @property
    def font_size(self):
        return int(self.params.get("font_size", 10))

    @property
    def scaled_font_size(self):
        return max(int(round((self.font_size * self.scale))), 1)

    @property
    def font_color(self):
        return self.params.get("font_color", "#000000")

    @property
    def back_color(self):
        return self.params.get("back_color", "#FFFFFF00")

    @property
    def focuser_fill_color(self):
        return self.params.get("focuser_fill_color", "#FF0000")

    @property
    def ppi(self):
        return int(self.params.get("ppi", 340))

    @property
    def padding(self):
        return int(self.params.get("padding", 0))

    @property
    def duration(self):
        return self.params["duration"]

    @property
    def font_pixel_size(self):
        return int(round(self.scaled_font_size*self.ppi/self.INCH2PIXEL))

    def get_font_point_to_pixel(self, point_size):
        return int(round(point_size*self.ppi/self.INCH2PIXEL))

    def copy(self):
        return TextConfig(self.params)

    def get_json(self):
        data = dict(self.params)
        data['TYPE_NAME'] = self.TYPE_NAME
        return data

    @classmethod
    def create_from_json(cls, data):
        return cls(**data)
