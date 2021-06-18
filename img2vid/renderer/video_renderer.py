import time
import random
import logging
import traceback

import numpy
import PIL.Image
import moviepy.editor
from proglog import ProgressBarLogger


from ..slides import TextSlide, ImageSlide, VideoSlide
from ..slides.geom_slide import GeomSlide
from ..utils import ImageUtils
from .. import effects as SlideEffects

from ..utils import ImageUtils

from .text_slide_clip import TextSlideClip
from .image_slide_clip import ImageSlideClip
from .geom_slide_clip import GeomSlideClip
from .slide_renderer import SlideRenderer

class EffectTimeSlice:
    def __init__(self, effect, start_time, duration):
        self.effect = effect
        self.start_time = start_time
        self.duration = duration

    @property
    def end_time(self):
        if self.start_time is None or self.duration is None:
            return None
        return self.start_time + self.duration

    def shift_time(self, offset):
        if self.start_time is None:
            return
        self.start_time += offset

    def transform_image(self, image, rel_time, app_config):
        frac = rel_time/self.duration
        if isinstance(self.effect, SlideEffects.ScalePan):
            if image.width < app_config.video_render.width or \
                image.height < app_config.video_render.height:
                scale_x = app_config.video_render.width / image.width
                scale_y = app_config.video_render.height / image.height
                image = ImageUtils.same_scale(image, 1.1*max(scale_x, scale_y))

            rect = self.effect.get_rect_at(
                frac=frac,
                bound_width=image.width,
                bound_height=image.height,
                aspect_ratio=app_config.video_render.aspect_ratio)
            image = ImageUtils.crop(image, rect)
            image = ImageUtils.resize(
                image,
                app_config.video_render.width,
                app_config.video_render.height)
        elif isinstance(self.effect, SlideEffects.FadeIn):
            image = ImageUtils.set_alpha(
                image, self.effect.get_value_at(frac=frac))
        elif isinstance(self.effect, SlideEffects.FadeOut):
            image = ImageUtils.set_alpha(
                image, self.effect.get_value_at(frac=frac))
        return image


class SlideTimeSlice:
    _IdSeed = 0

    def __init__(self, slide, start_time, duration):
        self.slide = slide
        self.duration = duration
        self.start_time = start_time
        self.effect_slices = []
        self._cached_image = None
        self._id_num = SlideTimeSlice._IdSeed + 1
        SlideTimeSlice._IdSeed = SlideTimeSlice._IdSeed + 1

    @property
    def end_time(self):
        return self.start_time + self.duration

    @property
    def min_start_time(self):
        min_effect_start = 0
        for tslice in self.effect_slices:
            if tslice.start_time is not None:
                min_effect_start = min(min_effect_start, tslice.start_time)
        return self.start_time + min_effect_start

    @property
    def max_end_time(self):
        max_effect_end = self.duration
        for tslice in self.effect_slices:
            if tslice.end_time is not None:
                max_effect_end = max(max_effect_end, tslice.end_time)
        return self.start_time + max_effect_end

    @property
    def id_num(self):
        return self._id_num

    def __eq__(self, other):
        return isinstance(other, SlideTimeSlice) and self.id_num == other.id_num

    def __hash__(self):
        return hash("Slide{}".format(self._id_num))

    def clear_cache(self):
        self._cached_image = None

    def shift_time(self, offset):
        self.start_time = self.min_start_time + offset
        for tslice in self.effect_slices:
            tslice.shift_time(offset)
            if tslice.end_time is not None:
                self.duration = max(self.duration, tslice.end_time)
        for tslice in self.effect_slices:
            if tslice.start_time is None:
                tslice.start_time = 0
            if tslice.duration is None:
                tslice.duration = self.duration

    def add_effect(self, effect, start_time=None, duration=None):
        slice_effect = EffectTimeSlice(effect, start_time, duration)
        self.effect_slices.append(slice_effect)
        self.duration = self.max_end_time-self.min_start_time

    def get_image_at(self, rel_time, app_config):
        image = self._cached_image
        progress = rel_time/self.duration
        if not image:
            if isinstance(self.slide, TextSlide):
                render_info = SlideRenderer.build_text_slide(
                    self.slide, app_config.video_render, app_config.text, progress)
            elif isinstance(self.slide, VideoSlide):
                self.slide.current_pos = rel_time
                render_info = SlideRenderer.build_image_slide(
                    self.slide, app_config.video_render, app_config.image, progress)
            elif isinstance(self.slide, ImageSlide):
                render_info = SlideRenderer.build_image_slide(
                    self.slide, app_config.video_render, app_config.image, progress)
            else:
                return None
            self._cached_image = image

        image = render_info.image
        video_config = app_config.video_render
        if image.width != video_config.width or \
           image.height != video_config.height:
            image = ImageUtils.fit_full(image, video_config.width, video_config.height)

        for tslice in self.effect_slices:
            if rel_time > tslice.end_time or \
               rel_time < tslice.start_time:
                continue
            image = tslice.transform_image(
                image, rel_time-tslice.start_time, app_config)
        return image

class VideoRenderer1:
    RENDER_DELAY = 0.01

    def __init__(self, app_config):
        self._app_config = app_config
        self._frame_callback = None
        self.duration = 0
        self.slices = []
        self._last_frame_time = 0
        self._last_used_slices = set()

        config = app_config.video_render
        self._back_image = ImageUtils.create_blank(
            config.width, config.height, config.back_color)

    @property
    def last_frame_time(self):
        return self._last_frame_time

    def set_frame_callback(self, method):
        self._frame_callback = method

    def add_slide(self, slide, start_time, duration):
        tslice = SlideTimeSlice(slide, start_time, duration)
        self.slices.append(tslice)
        return tslice

    def auto_fit(self):
        start_offset = 0
        self.duration = 0
        for tslice in self.slices:
            start_offset = min(start_offset, tslice.min_start_time)
        for tslice in self.slices:
            tslice.shift_time(-start_offset)
            self.duration = max(self.duration, tslice.end_time)

    def get_image_at(self, time_pos):
        slices = []
        for tslice in self.slices:
            if tslice.end_time >= time_pos >= tslice.start_time:
                slices.append(tslice)

        final_img_buffer = numpy.array(self._back_image, dtype=numpy.uint8)

        used_slices = set()
        for tslice in reversed(slices):
            image = tslice.get_image_at(
                time_pos-tslice.start_time, self._app_config)
            if not image:
                continue
            used_slices.add(tslice)

            img_buffer = numpy.array(image, dtype=numpy.uint8)
            alpha_values = img_buffer[:, :, 3]/255
            if numpy.amin(alpha_values) < 1:
                for i in range(3):
                    img_buffer[:, :, i] = img_buffer[:, :, i]*alpha_values
            try:
                final_img_buffer = numpy.maximum(final_img_buffer, img_buffer)
            except ValueError:
                logging.getLogger(__name__).error(traceback.format_exc())
                logging.getLogger(__name__).info("Slide: %s", tslice.slide.get_json())
            img_buffer = None

        for tslice in self._last_used_slices-used_slices:
            tslice.clear_cache()
        self._last_used_slices.clear()
        self._last_used_slices.update(used_slices)

        return PIL.Image.fromarray(final_img_buffer.astype(numpy.uint8))

    def get_frame_at(self, time_pos):
        time.sleep(self.RENDER_DELAY)
        self._last_frame_time = max(time_pos, self._last_frame_time)
        if self._frame_callback:
            if not self._frame_callback():
                raise Exception("Video rendering is terminated!")
        image = self.get_image_at(time_pos)
        frame = numpy.array(image, dtype=numpy.uint8)
        frame = frame[:, :, :3]
        return frame

    def make_video(self, dest_filepath):
        self._last_frame_time = 0
        video_clip = moviepy.editor.VideoClip(
            self.get_frame_at, duration=self.duration)
        config = self._app_config.video_render
        video_clip.write_videofile(
            dest_filepath, fps=config.fps,
            codec=config.video_codec,
            preset=config.ffmpeg_preset,
            ffmpeg_params=config.ffmpeg_params,
            bitrate=config.bit_rate)

    @classmethod
    def create_from_project(cls, project, app_config):
        video_renderer = VideoRenderer(app_config)

        cropped_files = []
        for slide in project.slides:
            if slide.TYPE_NAME == ImageSlide.TYPE_NAME and slide.rect:
                cropped_files.append(slide.filepath)

        elapsed = 0
        for slide in project.slides:
            seffects = dict(slide.effects)

            sduration = 0
            if slide.TYPE_NAME == TextSlide.TYPE_NAME:
                sduration = app_config.text.duration
            elif slide.TYPE_NAME in (ImageSlide.TYPE_NAME, VideoSlide.TYPE_NAME):
                if slide.TYPE_NAME == VideoSlide.TYPE_NAME:
                    sduration = slide.duration
                else:
                    sduration = app_config.image.duration
                if slide.rect:
                    random.seed()
                    sduration = app_config.image.random_crop_duration
                elif slide.filepath in cropped_files:
                    sduration = app_config.image.crop_source_duration
                if not slide.rect and not slide.has_caption:
                    effect = SlideEffects.ScalePan.create_random(1, 6)
                    seffects[effect.TYPE_NAME] = effect
            if sduration == 0:
                continue

            tslice = video_renderer.add_slide(slide, elapsed, sduration)
            elapsed += sduration

            effect = seffects.pop(SlideEffects.ScalePan.TYPE_NAME, None)
            if effect:#ScalePan effect
                tslice.add_effect(effect)

            effect = seffects.pop(SlideEffects.FadeOut.TYPE_NAME, None)
            if effect:#FadeOut effect
                tslice.add_effect(effect, sduration, effect.duration)

            effect = seffects.pop(SlideEffects.FadeIn.TYPE_NAME, None)
            if effect:#FadeIn effect
                tslice.add_effect(effect, -effect.duration, effect.duration)


        video_renderer.auto_fit()
        return video_renderer




class VideoRenderLogger(ProgressBarLogger):
    def __init__(self, external_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._external_callback = external_callback

    def bars_callback(self, *args, **kwargs):
        if self._external_callback and \
           self.state.get('bars') and self.state['bars']['t']:
            t = self.state['bars']['t']
            self._external_callback(progress=t['index']/t['total'])

class VideoRenderer:
    RENDER_DELAY = 0.01

    def __init__(self, app_config):
        self._frame_callback = None
        self._app_config = app_config

        config = app_config.video_render
        self._back_image = ImageUtils.create_blank(
            config.width, config.height, config.back_color)

        self._outer_clip = None
        self._clips = []
        self.screen_size = (800, 600)

    @property
    def last_frame_time(self):
        return self._outer_clip.duration

    @property
    def duration(self):
        return self.outer_clip.duration

    def set_frame_callback(self, method):
        self._frame_callback = method

    def append_clip(self, clip):
        self._clips.append(clip)

    @property
    def outer_clip(self):
        if not self._outer_clip:
            self._outer_clip = moviepy.editor.CompositeVideoClip(
                self._clips,
                size=self.screen_size
            )
        return self._outer_clip

    def get_image_at(self, time_pos):
        time_pos = min(time_pos, self.duration)
        data = self.outer_clip.get_frame(time_pos)
        try:
            return PIL.Image.fromarray(data)
        except Exception as ex:
            print("data", data)
            raise ex

    def get_frame_at(self, time_pos):
        time.sleep(self.RENDER_DELAY)
        if self._frame_callback:
            if not self._frame_callback():
                raise Exception("Video rendering is terminated!")
        image = self.get_image_at(time_pos)
        frame = numpy.array(image, dtype=numpy.uint8)
        frame = frame[:, :, :3]
        return frame

    def make_video(self, dest_filepath, callback = None):
        config = self._app_config.video_render
        if callback:
            render_logger = VideoRenderLogger(external_callback=callback)
        else:
            render_logger = 'bar'
        self.outer_clip.write_videofile(
            dest_filepath, fps=config.fps,
            codec=config.video_codec,
            preset=config.ffmpeg_preset,
            ffmpeg_params=config.ffmpeg_params,
            bitrate=config.bit_rate,
            logger=render_logger)


    def create_clip(self, slide, app_config, **kwargs):
        clip = None
        if slide.TYPE_NAME == TextSlide.TYPE_NAME:
            clip = TextSlideClip(slide, app_config, size=self.screen_size, **kwargs)
        elif slide.TYPE_NAME == ImageSlide.TYPE_NAME:
            clip = ImageSlideClip(slide, app_config, size=self.screen_size, **kwargs)
        elif slide.TYPE_NAME.endswith(GeomSlide.TYPE_NAME):
            clip = GeomSlideClip(slide, app_config, size=self.screen_size, **kwargs)
        return clip

    @classmethod
    def create_from_project(cls, project, app_config):
        video_renderer = VideoRenderer(app_config)

        cropped_files = []
        for slide in project.slides:
            if slide.TYPE_NAME == ImageSlide.TYPE_NAME and slide.rect:
                cropped_files.append(slide.filepath)

        clips = []

        video_renderer.screen_size =(
            app_config.video_render.scaled_width,
            app_config.video_render.scaled_height
        )

        elapsed = 0
        for slide in project.slides:
            seffects = dict(slide.effects)

            sduration = slide.duration
            if slide.TYPE_NAME == TextSlide.TYPE_NAME:
                sduration = app_config.text.duration
            elif slide.TYPE_NAME in (ImageSlide.TYPE_NAME, VideoSlide.TYPE_NAME):
                if slide.TYPE_NAME == VideoSlide.TYPE_NAME:
                    sduration = slide.duration
                else:
                    sduration = app_config.image.duration
                if slide.rect:
                    random.seed()
                    sduration = app_config.image.random_crop_duration
                elif slide.filepath in cropped_files:
                    sduration = app_config.image.crop_source_duration
                if not slide.rect and not slide.has_caption:
                    effect = SlideEffects.ScalePan.create_random(1, 6)
                    seffects[effect.TYPE_NAME] = effect
            elif slide.TYPE_NAME.endswith(GeomSlide.TYPE_NAME):
                sduration = app_config.image.duration

            if not sduration:
                continue

            clip = video_renderer.create_clip(slide, app_config)
            if not clip:
                continue

            clip.duration = sduration

            effect = seffects.pop(SlideEffects.ScalePan.TYPE_NAME, None)
            if effect:#ScalePan effect
                pass

            effect = seffects.pop(SlideEffects.FadeOut.TYPE_NAME, None)
            if effect:#FadeOut effect
                clip = clip.fx(moviepy.video.fx.all.fadeout, duration=effect.duration, final_color=0)

            effect = seffects.pop(SlideEffects.FadeIn.TYPE_NAME, None)
            if effect:#FadeIn effect
                clip = clip.fx(moviepy.video.fx.all.fadein, duration=effect.duration)

            clip = clip.set_start(max(0, elapsed))
            clip = clip.crossfadein(.5)


            if slide.mask_slide:
                mask_clip = video_renderer.create_clip(slide.mask_slide, app_config,
                    ismask=True, duration=clip.duration)
                mask_clip = mask_clip.set_start(clip.start)
                clip = clip.set_mask(mask_clip)

            if slide.sub_slides:
                for sub_slide in slide.sub_slides:
                    sub_clip = video_renderer.create_clip(
                        sub_slide, app_config,
                        start=clip.start + (sub_slide.delay or 0),
                        duration=(sub_slide.duration or (clip.duration - (sub_slide.delay or 0)))
                    )
                    clip.add_sub_clip(sub_clip)

            video_renderer.append_clip(clip)

            elapsed += sduration

        return video_renderer
