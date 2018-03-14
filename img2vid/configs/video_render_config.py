class VideoRenderConfig:
    def __init__(self, **kwargs):
        self.params = dict(kwargs)
        self._scale = 1

    @property
    def scaled_width(self):
        return int(self.width*self.scale)

    @property
    def scaled_height(self):
        return int(self.height*self.scale)

    @property
    def scale(self):
        return self.params.get("scale", 1)

    @scale.setter
    def scale(self, value):
        self.params["scale"] = value

    @property
    def width(self):
        return self.params["width"]

    @property
    def height(self):
        return self.params["height"]

    @property
    def aspect_ratio(self):
        return self.params["width"]/self.params["height"]

    @property
    def back_color(self):
        return self.params["back_color"]

    @property
    def ffmpeg_params(self):
        return self.params["ffmpeg_params"]

    @property
    def bit_rate(self):
        return self.params["bit_rate"]

    @property
    def ffmpeg_preset(self):
        return self.params["ffmpeg_preset"]

    @property
    def video_codec(self):
        return self.params["video_codec"]

    @property
    def fps(self):
        return self.params["fps"]

    @property
    def video_ext(self):
        return self.params["video_ext"]

    def get_json(self):
        return dict(self.params)

    def copy(self):
        return VideoRenderConfig(self.params)

    @classmethod
    def create_from_json(cls, data):
        return cls(**data)
