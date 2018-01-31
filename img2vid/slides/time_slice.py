from commons import ScalePan, Point
from .text_slide import TextSlide
from .image_slide import ImageSlide

class TimeSlice:
    def __init__(self, slide):
        self.slide = slide
        self.duration = 0
        self.scale_pan = None
        self.image = None

    def serialize(self):
        data = dict(slide=self.slide, duration=self.duration)
        if self.scale_pan:
            data["scale_pan"] = self.scale_pan.serialize()
        return data

    @classmethod
    def create_from_data(cls, data):
        slide_type = data["slide"]["type"]
        if slide_type == TextSlide.TypeName:
            slide = TextSlide.create_from_data(data["slide"])
        else:
            slide = ImageSlide.create_from_data(data["slide"])
        slide = cls(slide)
        slide.set_duration(data["duration"])
        if "scale_pan" in data:
            slide.set_scale_pan(ScalePan.create_from_data(data["scale_pan"]))
        return slide

    def set_duration(self, duration):
        self.duration = duration

    def set_scale_pan(self, scale_pan):
        self.scale_pan = scale_pan

    def process(self, image, t, resolution):
        if not self.scale_pan:
            return (image, False)
        frac = t/self.duration
        clearance = 10
        rect = self.scale_pan.get_view_rect(
            frac,
            image.width-clearance, image.height-clearance,
            resolution.get_ratio())
        rect.translate(Point(clearance, clearance))
        image=image.crop((rect.x1, rect.y1, rect.x2, rect.y2))
        return (image, True)