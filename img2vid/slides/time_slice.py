from commons import ScalePan

class TimeSlice:
    def __init__(self, slide):
        self.slide = slide
        self.duration = 0
        self.scale_pan = None
        self.image = None

    def set_duration(self, duration):
        self.duration = duration

    def set_scale_pan(self, scale_pan):
        self.scale_pan = scale_pan

    def process(self, image, t):
        if not self.scale_pan:
            return image
        frac = t/self.duration
        rect = self.scale_pan.get_view_rect(frac, image.width/image.height)
        rect.scale(image.width, image.height)
        image=image.crop((rect.x1, rect.y1, rect.x2, rect.y2))
        return image