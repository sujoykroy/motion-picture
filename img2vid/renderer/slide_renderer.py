import wand.image
import wand.drawing
import wand.color

from ..geom import Rectangle, Point
from ..utils import ImageUtils
from ..effects import Effect
from ..slides import ImageSlide, VideoSlide, TextSlide
from ..analysers import TextAnalyser

from .render_info import RenderInfo
from .caption_renderer import CaptionRenderer


class ImageSlideBuilder:
    def __init__(self, slide):
        self.slide = slide
        self.captions = slide.active_captions
        self.orig_image_scale = 1
        self.cap_images = {}
        self.total_cap_height = 0
        self.draw_top = 0
        self.draw_bottom = 0

    def fetch_image(self, progress):
        wand_image = bool(self.captions)
        if self.slide.TYPE_NAME == VideoSlide.TYPE_NAME:
            self.file_image = ImageUtils.fetch_video_frame(
                filepath=self.slide.filepath,
                time_pos=self.slide.abs_current_pos,
                crop=self.slide.rect, wand_image=False)
        else:
            self.file_image = ImageUtils.fetch_image(
                filepath=self.slide.local_filepath,
                crop=self.slide.rect, wand_image=False)

        if self.slide.effects and False:
            for effect in self.slide.effects.values():
                # print(effect.TYPE_NAME, effect.APPLY_ON & Effect.APPLY_TYPE_TEXT)
                if self.slide.TYPE_NAME == TextSlide.TYPE_NAME and \
                   (effect.APPLY_ON & Effect.APPLY_TYPE_TEXT) == 0:
                    continue
                if self.slide.TYPE_NAME == ImageSlide.TYPE_NAME and \
                   (effect.APPLY_ON & Effect.APPLY_TYPE_IMAGE) == 0:
                    continue
                if self.slide.TYPE_NAME == VideoSlide.TYPE_NAME and \
                   (effect.APPLY_ON & Effect.APPLY_TYPE_VIDEO) == 0:
                    continue
                self.file_image = effect.transform(
                    image=self.file_image, progress=progress,
                    slide=self.slide)

        if wand_image:
            self.file_image = ImageUtils.pil2wand(self.file_image)

    def get_min_img_height(self, screen_config, image_config):
        max_img_height = screen_config.scaled_height
        for caption in self.captions:
            caption_metric = TextAnalyser.get_font_metric(caption, image_config)

            if caption.valign != ImageSlide.CAP_ALIGN_CENTER:
                max_img_height -= caption_metric.height
        return max_img_height

    def fit_file_image(self, screen_config, max_img_height):
        fitted_image = ImageUtils.fit_inside(
            self.file_image, screen_config.scaled_width, max_img_height)
        self.orig_image_scale = fitted_image.width/self.file_image.width
        self.file_image = fitted_image
        del fitted_image

    def build_caption_images(self, image_config):
        #Build caption-images and store total cap height
        self.total_cap_height = 0
        self.cap_images.clear()
        for caption in self.captions:
            cap_image = CaptionRenderer.caption2image(
                caption=caption, min_width=0,
                text_config=image_config, wand_image=True)
            if caption.valign != ImageSlide.CAP_ALIGN_CENTER:
                self.total_cap_height += cap_image.height
            self.cap_images[caption.valign] = cap_image

    def build_draw_area(self, screen_config):
        #Determine drawing top/bottom
        self.draw_top = int((screen_config.scaled_height-\
                    self.file_image.height-self.total_cap_height)*0.5)
        self.draw_bottom = self.draw_top + self.file_image.height + self.total_cap_height

class SlideRenderer:
    @classmethod
    def build_text_slide(cls, slide, screen_config, text_config, progress=1):
        back_color = slide.caption.back_color or text_config.back_color
        with wand.image.Image(resolution=text_config.ppi,
                              background=wand.color.Color(back_color),
                              width=screen_config.scaled_width,
                              height=screen_config.scaled_height) as canvas:
            canvas.units = ImageUtils.PIXEL_PER_INCH
            with wand.drawing.Drawing() as context:
                # Place caption images
                cap_image = CaptionRenderer.caption2image(
                    caption=slide.caption, min_width=0,
                    text_config=text_config, wand_image=True
                )
                cap_pos = Point(
                    (screen_config.scaled_width - cap_image.width) * 0.5,
                    (screen_config.scaled_height - cap_image.height) * 0.5
                )
                cap_pos.x = int(cap_pos.x)
                cap_pos.y = int(cap_pos.y)
                canvas.composite(image=cap_image, left=cap_pos.x, top=cap_pos.y)
                image = ImageUtils.wand2pil(canvas)
        return RenderInfo(image)

    @classmethod
    def build_image_slide(cls, slide, screen_config, image_config, progress=1):
        builder = ImageSlideBuilder(slide)
        builder.fetch_image(progress)

        if not builder.captions:
            return RenderInfo(builder.file_image)

        with wand.image.Image(resolution=image_config.ppi,
                              width=screen_config.scaled_width,
                              height=screen_config.scaled_height) as canvas:
            canvas.units = ImageUtils.PIXEL_PER_INCH
            with wand.drawing.Drawing() as context:
                builder.fit_file_image(
                    screen_config,
                    screen_config.height)
                builder.build_caption_images(image_config)
                builder.build_draw_area(screen_config)

                # Place the file image
                img_pos = Point(
                    int((screen_config.scaled_width-builder.file_image.width)*0.5),
                    int((screen_config.scaled_height-builder.file_image.height)*0.5))
                img_pos.x = int(img_pos.x)
                img_pos.y = int(img_pos.y)
                canvas.composite(image=builder.file_image, left=img_pos.x, top=img_pos.y)

                # Place caption images
                for cap_align, cap_image in builder.cap_images.items():
                    cap_pos = Point((screen_config.scaled_width-cap_image.width)*0.5, 0)
                    if cap_align == ImageSlide.CAP_ALIGN_CENTER:
                        cap_pos.y = (screen_config.scaled_height - cap_image.height)  *0.5
                    elif cap_align == ImageSlide.CAP_ALIGN_TOP:
                        cap_pos.y = 0
                    elif cap_align == ImageSlide.CAP_ALIGN_BOTTOM:
                        cap_pos.y = screen_config.scaled_height - cap_image.height
                    cap_pos.x = int(cap_pos.x)
                    cap_pos.y = int(cap_pos.y)
                    canvas.composite(image=cap_image, left=cap_pos.x, top=cap_pos.y)
                context(canvas)
                image = ImageUtils.wand2pil(canvas)

        editable_rect = Rectangle(
            img_pos.x, img_pos.y,
            img_pos.x+builder.file_image.width, img_pos.y+builder.file_image.height)
        return RenderInfo(image, editable_rect, builder.orig_image_scale)
