import numpy
from PIL import Image, ImageDraw

from commons import ScalePan, Point
from .slide import Slide
from .text_slide import TextSlide
from .image_slide import ImageSlide

class TimeSlice:
    def __init__(self, slide, config):
        self.slide = slide
        self.scale_pan = None
        self.image = None

        self.abs_time_offset = 0
        self.pre_trans_dur = 0
        self.post_trans_dur = 0
        if Slide.FILTER_FADE_IN in slide.filters:
            self.pre_trans_dur = config.fade_in_duration
        if Slide.FILTER_FADE_OUT in slide.filters:
            self.post_trans_dur = config.fade_out_duration
        self.main_duration = 0
        self.set_main_duration(0)

    def set_abs_time_offset(self, value):
        self.abs_time_offset = value

    def set_main_duration(self, duration):
        self.main_duration = duration
        self.total_duration = self.main_duration+self.pre_trans_dur+self.post_trans_dur

    def is_within(self, t):
        return self.abs_time_offset<=t<=self.abs_time_offset+self.total_duration

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

    def set_scale_pan(self, scale_pan):
        self.scale_pan = scale_pan

    def process(self, image, t, config):
        rel_t = t - self.abs_time_offset
        resolution = config.video_resolution
        if self.scale_pan:
            image = image.copy()
            if image.width<resolution.x:
                sc = max(resolution.x/image.width, resolution.y/image.height)
                sc *= 1.1
                image = image.resize((int(image.width*sc), int(image.height*sc)), resample=True)

            frac = rel_t/self.total_duration
            clearance = 10
            rect = self.scale_pan.get_view_rect(
                frac,
                image.width-2*clearance, image.height-2*clearance,
                resolution.get_ratio())
            rect.translate(Point(clearance, clearance))

            if config.video_debug:
                draw = ImageDraw.Draw(image)
                points = self.scale_pan.get_polygon_points(
                    image.width-2*clearance, image.height-2*clearance,
                    resolution.get_ratio())

                for i in range(len(points)):
                    point = points[i]
                    point.add(Point(clearance, clearance))
                    points[i] = (point.x, point.y)
                draw.line(points, width=1, fill="#FFFFFF")
                draw.rectangle([rect.x1, rect.y1, rect.x2, rect.y2], outline="#FFFFFF")
                cx = rect.get_cx()
                cy = rect.get_cy()
                draw.ellipse([cx-2, cy-2, cx+2, cy+2], outline="#FFFFFF")
                del draw
            else:
                image = image.crop((rect.x1, rect.y1, rect.x2, rect.y2))
                image = image.resize((resolution.x, resolution.y), resample=True)

        if self.pre_trans_dur and rel_t<self.pre_trans_dur:
            alpha_frac = rel_t/self.pre_trans_dur
        elif self.post_trans_dur and rel_t>self.pre_trans_dur+self.main_duration:
            alpha_frac = 1-((rel_t-self.pre_trans_dur-self.main_duration)/self.post_trans_dur)
        else:
            alpha_frac = 1
        if alpha_frac != 1:
            container = Image.new("RGBA", (image.width, image.height))
            container.paste(image, (0, 0))
            image = container
            img_buffer = numpy.array(image, dtype=numpy.uint8)
            img_buffer[:,:,:3] = img_buffer[:,:,:3]*alpha_frac
            img_buffer.dtype = numpy.uint8
            image = Image.fromarray(img_buffer)
        return image
