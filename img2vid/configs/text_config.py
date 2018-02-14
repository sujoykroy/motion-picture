class TextConfig:
    INCH2PIXEL = 72

    def __init__(self, **kwargs):
        self.params = dict(kwargs)

    @property
    def font_name(self):
        return self.params.get("font_name")

    @property
    def font_size(self):
        return int(self.params.get("font_size", 10))

    @property
    def font_color(self):
        return self.params.get("font_color", "#000000")

    @property
    def back_color(self):
        return self.params.get("back_color", "#FFFFFF00")

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
        return int(round(self.font_size*self.ppi/self.INCH2PIXEL))
