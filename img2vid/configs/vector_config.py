import random

class VectorConfig:
    TYPE_NAME = 'image_config'

    def __init__(self, **kwargs):
        self.params = dict(kwargs)

    @property
    def stroke_width(self):
        return self.params.get("stroke_width", 1)

    @property
    def fill_color(self):
        return self.params.get("fill_color", "#FFFFFF")

    @property
    def border_color(self):
        return self.params.get("border_color", None)

    def copy(self):
        return VectorConfig(self.params)
