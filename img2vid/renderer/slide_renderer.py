import wand.image
import wand.drawing
import wand.color

from ..slides import ImageSlide, VideoSlide
from ..analysers import TextAnalyser
from .render_info import RenderInfo
from .image_renderer import ImageRenderer
from ..geom import Rectangle, Point

class ImageSlideBuilder:
    def __init__(self, slide):
        self.slide = slide
        self.captions = slide.active_captions
        self.orig_image_scale = 1
        self.cap_images = {}
        self.total_cap_height = 0
        self.draw_top = 0
        self.draw_bottom = 0

    def fetch_image(self):
        wand_image = bool(self.captions)
        if self.slide.TYPE_NAME == VideoSlide.TYPE_NAME:
            self.file_image = ImageRenderer.fetch_video_frame(
                filepath=self.slide.filepath,
                time_pos=self.slide.abs_current_pos,
                crop=self.slide.rect, wand_image=wand_image)
        else:
            self.file_image = ImageRenderer.fetch_image(
                filepath=self.slide.filepath,
                crop=self.slide.rect, wand_image=wand_image)

    def get_min_img_height(self, screen_config, image_config):
        max_img_height = screen_config.height
        for caption in self.captions:
            caption_metric = TextAnalyser.get_font_metric(caption, image_config)

            if caption.valign != ImageSlide.CAP_ALIGN_CENTER:
                max_img_height -= caption_metric.height
        return max_img_height

    def fit_file_image(self, screen_config, max_img_height):
        fitted_image = ImageRenderer.fit_inside(
            self.file_image, screen_config.width, max_img_height)
        self.orig_image_scale = fitted_image.width/self.file_image.width
        self.file_image = fitted_image
        del fitted_image

    def build_caption_images(self, image_config):
        #Build caption-images and store total cap height
        self.total_cap_height = 0
        self.cap_images.clear()
        for caption in self.captions:
            cap_image = ImageRenderer.caption2image(
                caption=caption, min_width=self.file_image.width,
                text_config=image_config, wand_image=True)
            if caption.valign != ImageSlide.CAP_ALIGN_CENTER:
                self.total_cap_height += cap_image.height
            self.cap_images[caption.valign] = cap_image

    def build_draw_area(self, screen_config):
        #Determine drawing top/bottom
        self.draw_top = int((screen_config.height-\
                    self.file_image.height-self.total_cap_height)*0.5)
        self.draw_bottom = self.draw_top + self.file_image.height + self.total_cap_height


class SlideRenderer:
    @classmethod
    def build_text_slide(cls, slide, screen_config, text_config):
        back_color = slide.caption.back_color or text_config.back_color
        with wand.image.Image(resolution=text_config.ppi,
                              background=wand.color.Color(back_color),
                              width=screen_config.width,
                              height=screen_config.height) as canvas:
            canvas.units = ImageRenderer.PIXEL_PER_INCH
            with wand.drawing.Drawing() as context:
                ImageRenderer.apply_caption(context, slide.caption, text_config)
                context.gravity = "center"
                context.text(x=0, y=0, body=slide.caption.text)
                context(canvas)
                image = ImageRenderer.wand2pil(canvas)
        return RenderInfo(image)

    @classmethod
    def build_image_slide(cls, slide, screen_config, image_config):
        builder = ImageSlideBuilder(slide)
        builder.fetch_image()

        if not builder.captions:
            return RenderInfo(builder.file_image)

        with wand.image.Image(resolution=image_config.ppi,
                              width=screen_config.width,
                              height=screen_config.height) as canvas:
            canvas.units = ImageRenderer.PIXEL_PER_INCH
            with wand.drawing.Drawing() as context:
                builder.fit_file_image(
                    screen_config,
                    builder.get_min_img_height(screen_config, image_config))
                builder.build_caption_images(image_config)
                builder.build_draw_area(screen_config)

                #Place the file image
                img_pos = Point(
                    int((screen_config.width-builder.file_image.width)*0.5),
                    int((screen_config.height-builder.file_image.height)*0.5))
                if ImageSlide.CAP_ALIGN_TOP in builder.cap_images:
                    img_pos.y = builder.cap_images[ImageSlide.CAP_ALIGN_TOP].height
                elif ImageSlide.CAP_ALIGN_BOTTOM in builder.cap_images:
                    img_pos.y = builder.draw_bottom - \
                                builder.file_image.height - \
                                builder.cap_images[ImageSlide.CAP_ALIGN_BOTTOM].height
                img_pos.x = int(img_pos.x)
                img_pos.y = int(img_pos.y)
                canvas.composite(image=builder.file_image, left=img_pos.x, top=img_pos.y)

                #Place caption images
                for cap_align, cap_image in builder.cap_images.items():
                    cap_pos = Point((screen_config.width-cap_image.width)*0.5, 0)
                    if cap_align == ImageSlide.CAP_ALIGN_CENTER:
                        cap_pos.y = img_pos.y + (builder.file_image.height - cap_image.height)*0.5
                    elif cap_align == ImageSlide.CAP_ALIGN_TOP:
                        cap_pos.y = builder.draw_top
                    elif cap_align == ImageSlide.CAP_ALIGN_BOTTOM:
                        cap_pos.y = builder.draw_bottom - cap_image.height
                    cap_pos.x = int(cap_pos.x)
                    cap_pos.y = int(cap_pos.y)
                    canvas.composite(image=cap_image, left=cap_pos.x, top=cap_pos.y)
                context(canvas)
                image = ImageRenderer.wand2pil(canvas)
        editable_rect = Rectangle(
            img_pos.x, img_pos.y,
            img_pos.x+builder.file_image.width, img_pos.y+builder.file_image.height)
        return RenderInfo(image, editable_rect, builder.orig_image_scale)
