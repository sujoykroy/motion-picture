import random
import numpy
import time
from PIL import Image

from moviepy.editor import VideoClip

from commons import Point, ScalePan

from .time_slice import TimeSlice
from .image_slide import ImageSlide
from .text_slide import TextSlide


class VideoFrameMaker:
    def __init__(self, slides, config):
        self.config = config
        self.duration = 0
        self.resolution = config.video_resolution
        self.time_slices = []
        self.last_used_slides = {}
        self.last_max_t = 0
        self.delay = 0
        self.make_frame_callback = None

        cropped_files = []
        for i in range(len(slides)):
            slide = slides[i]
            if slide.TypeName == ImageSlide.TypeName and slide.rect:
                cropped_files.append(slide.get_filepath)

        for i in range(len(slides)):
            slide = slides[i]
            time_slice = TimeSlice(slide=slide, config=self.config)
            if i==0 and time_slice.pre_trans_dur>0:
                self.duration += time_slice.pre_trans_dur
            time_slice.set_abs_time_offset(self.duration-time_slice.pre_trans_dur)

            if slide.TypeName == TextSlide.TypeName:
                duration = config.get_param("text-slide-durtion", 3)
            elif slide.rect:
                random.seed()
                duration = config.get_param("cropped-image-durtion", 1+random.random())
            elif slide.get_filepath() in cropped_files:
                duration = config.get_param("crop-orig-image-durtion", 3)
            else:
                if not slide.get_caption():
                    time_slice.set_scale_pan(ScalePan.create_random(1, 6))
                duration = config.get_param("image-durtion", 5)

            time_slice.set_main_duration(duration)
            self.time_slices.append(time_slice)
            self.duration += duration

        self.duration += self.time_slices[-1].post_trans_dur

    def serialize(self):
        data = dict(slices=[])
        for slice in self.time_slices:
            data["slices"].append(slice.serialize())
        return data

    @classmethod
    def create_from_data(cls, data, config):
        ob = cls(slides=[], config=config)
        for slice in data["slices"]:
            slice = TimeSlice.create_from_data(slice)
            ob.time_slices.append(slice)
            ob.duration += slice.duration
        return ob

    def get_image_at(self, t):
        elapsed = 0
        active_time_slices = []
        for tm in self.time_slices:
            if tm.is_within(t):
                active_time_slices.append(tm)



        final_img_buffer = None
        used_slides = {}
        for time_slice in (active_time_slices):
            if time_slice.slide not in self.last_used_slides:
                image = time_slice.slide.get_renderable_image(self.config)
            else:
                image = self.last_used_slides[time_slice.slide]
            used_slides[time_slice.slide] = image

            image = time_slice.process(image, t, self.config)

            container = Image.new("RGBA",
                                  (self.resolution.x, self.resolution.y),
                                  self.config.video_background_color)
            sx = self.resolution.x/image.width
            sy = self.resolution.y/image.height
            sc = min(sx, sy)
            image = image.resize(
                (int(round(image.width*sc)), int(round(image.height*sc))), resample=True)

            ofx = int((self.resolution.x-image.width)*0.5)
            ofy = int((self.resolution.y-image.height)*0.5)
            container.paste(image, (ofx, ofy))

            img_buffer = numpy.array(container, dtype=numpy.uint8)
            if final_img_buffer is None:
                final_img_buffer = img_buffer
            else:
                final_img_buffer = numpy.maximum(final_img_buffer, img_buffer)

        self.last_used_slides.clear()
        self.last_used_slides.update(used_slides)

        return Image.fromarray(final_img_buffer.astype(numpy.uint8))

    def make_frame(self, t):
        time.sleep(self.delay)
        self.last_max_t = max(t, self.last_max_t)
        if self.make_frame_callback:
            if not self.make_frame_callback():
                raise Exception("Terminate Now!")
        image = self.get_image_at(t)
        data = numpy.array(image, dtype=numpy.uint8)
        data = data[:,:, :3]
        return data

    def make_video(self, dest, config):
        self.last_max_t = 0
        video_clip = VideoClip(self.make_frame, duration=self.duration)
        video_clip.write_videofile(dest, fps=config.fps, codec=config.video_codec,
                                   preset=config.ffmpeg_preset,
                                   ffmpeg_params=config.ffmpeg_params,
                                   bitrate=config.bit_rate)
