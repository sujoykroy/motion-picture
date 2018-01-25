import random
from PIL import Image

from commons import Point

from .time_slice import TimeSlice
from .image_slide import ImageSlide
from .text_slide import TextSlide
from .linear_change import LinearChange

class VideoFrameMaker:
    def __init__(self, slides, config):
        self.config = config
        self.duration = 0
        self.resolution = Point(*config.get_video_resolution())
        self.time_slices = []
        self.last_used_slide = None
        self.last_slide_image = None

        cropped_files = []
        for i in range(len(slides)):
            slide = slides[i]
            if slide.TypeName == ImageSlide.TypeName and slide.rect:
                cropped_files.append(slide.get_filepath)

        for i in range(len(slides)):
            slide = slides[i]
            time_slice = TimeSlice(slide=slide)

            if slide.TypeName == TextSlide.TypeName:
                duration = config.get_param("text-slide-durtion", 3)
            elif slide.rect:
                random.seed()
                duration = config.get_param("cropped-image-durtion", 1+random.random())
            elif slide.get_filepath() in cropped_files:
                duration = config.get_param("crop-orig-image-durtion", 3)
            else:
                duration = config.get_param("image-durtion", 5)
                random.seed()
                if random.choice([True, False]):
                    zoom_change = LinearChange(1, random.random()*.5)
                else:
                    zoom_change = LinearChange(random.random()*.5, 1)
                time_slice.set_params_change("zoom", zoom_change)
                time_slice.set_params_change(
                    "cx", LinearChange(random.random(), random.random()))
                time_slice.set_params_change(
                    "cy", LinearChange(random.random(), random.random()))
            time_slice.set_duration(duration)
            self.time_slices.append(time_slice)
            self.duration += duration

    def get_image_at(self, t):
        elapsed = 0
        time_slice = None
        for tm in self.time_slices:
            if t<elapsed+tm.duration:
                time_slice = tm
                break
            elapsed += tm.duration
        if not time_slice:
            time_slice = self.time_slices[-1]
            rel_t = time_slice.duration
        else:
            rel_t = t - elapsed

        if time_slice.slide != self.last_used_slide:
            self.last_slide_image = time_slice.slide.get_renderable_image(
                                            self.resolution, self.config)

        self.last_used_slide = time_slice.slide
        image = self.last_slide_image

        sx = self.resolution.x/image.width
        sy = self.resolution.y/image.height
        sc = min(sx, sy)
        image = image.resize((int(image.width*sc), int(image.height*sc)), resample=True)

        ofx = int((self.resolution.x-image.width)*0.5)
        ofy = int((self.resolution.y-image.height)*0.5)

        container = Image.new("RGBA",
                              (self.resolution.x, self.resolution.y),
                              self.config.video_background_color)
        container.paste(image, (ofx, ofy))
        image = container
        return image
