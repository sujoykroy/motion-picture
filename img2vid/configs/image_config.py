import random
from .text_config import TextConfig

class ImageConfig(TextConfig):
    @property
    def min_crop_duration(self):
        return self.params["min_crop_duration"]

    @property
    def max_crop_duration(self):
        return self.params["max_crop_duration"]

    @property
    def crop_source_duration(self):
        return self.params["crop_source_duration"]

    @property
    def random_crop_duration(self):
        diff = self.params["max_crop_duration"]-self.params["min_crop_duration"]
        return self.params["min_crop_duration"]+random.random()*diff
