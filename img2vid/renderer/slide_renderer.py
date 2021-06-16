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
from .vector_renderer import VectorRenderer
from ..configs.vector_config import VectorConfig


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
                    caption=slide.caption, max_width=screen_config.scaled_width,
                    text_config=text_config, wand_image=True
                )
                if cap_image:
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
    def build_image_slide(cls, slide, screen_config, image_config):
        render_info = cls.build_image_slide_only_image(slide, screen_config, image_config)
        file_image= ImageUtils.pil2wand(render_info.image)

        image = cls.build_image_slide_only_captions(
            slide, screen_config, image_config, render_info.image
        )

        return RenderInfo(image, render_info.editable_rect, render_info.orig_image_scale)

    @classmethod
    def build_image_slide_only_captions(cls, slide, screen_config, image_config, canvas):
        with wand.drawing.Drawing() as context:
            canvas= ImageUtils.pil2wand(canvas)
            canvas.units = ImageUtils.PIXEL_PER_INCH

            for caption in slide.active_captions:
                cap_image = CaptionRenderer.caption2image(
                    caption=caption, max_width=screen_config.scaled_width,
                    text_config=image_config, wand_image=True
                )
                if not cap_image:
                    continue
                cap_pos = Point(0, 0)

                margin = caption.margin

                valign = caption.valign
                if valign == ImageSlide.CAP_ALIGN_CENTER:
                    cap_pos.y = (screen_config.scaled_height - cap_image.height - 2 * margin)  *0.5
                elif valign == ImageSlide.CAP_ALIGN_TOP:
                    cap_pos.y = margin
                elif valign == ImageSlide.CAP_ALIGN_BOTTOM:
                    cap_pos.y = screen_config.scaled_height - cap_image.height - margin

                halign = caption.halign
                if halign == ImageSlide.CAP_ALIGN_LEFT:
                    cap_pos.x = margin
                elif halign == ImageSlide.CAP_ALIGN_RIGHT:
                    cap_pos.x = screen_config.scaled_width - cap_image.width - margin
                elif halign == ImageSlide.CAP_ALIGN_CENTER:
                    cap_pos.x =  (screen_config.scaled_width - cap_image.width -2 * margin)  *0.5

                cap_pos.x = int(cap_pos.x)
                cap_pos.y = int(cap_pos.y)
                canvas.composite(image=cap_image, left=cap_pos.x, top=cap_pos.y)

                if caption.focuser:
                    foucer_image, focuser_pos = CaptionRenderer.create_focuser_image(
                        caption, cap_image, cap_pos, wand_image=True
                    )
                    canvas.composite(image=foucer_image, left=focuser_pos.x, top=focuser_pos.y)

            context(canvas)
            canvas = ImageUtils.wand2pil(canvas)

        return canvas

    @classmethod
    def build_image_slide_only_image(cls, slide, screen_config, image_config):
        if slide.TYPE_NAME == VideoSlide.TYPE_NAME:
            file_image = ImageUtils.fetch_video_frame(
                filepath=slide.filepath,
                time_pos=slide.abs_current_pos,
                crop=slide.rect, wand_image=False)
        else:
            file_image = ImageUtils.fetch_image(
                filepath=slide.local_filepath,
                crop=slide.rect, wand_image=False)

        fitted_image = ImageUtils.fit_inside(
            file_image, screen_config.scaled_width, screen_config.scaled_height)

        orig_image_scale = fitted_image.width/file_image.width
        file_image= ImageUtils.pil2wand(fitted_image)

        with wand.image.Image(resolution=image_config.ppi,
                              width=screen_config.scaled_width,
                              height=screen_config.scaled_height) as canvas:
            canvas.units = ImageUtils.PIXEL_PER_INCH

            with wand.drawing.Drawing() as context:
                # Place the file image
                img_pos = Point(
                    int((screen_config.scaled_width-file_image.width)*0.5),
                    int((screen_config.scaled_height-file_image.height)*0.5))
                img_pos.x = int(img_pos.x)
                img_pos.y = int(img_pos.y)
                canvas.composite(image=file_image, left=img_pos.x, top=img_pos.y)
                image = ImageUtils.wand2pil(canvas)

        editable_rect = Rectangle(
            img_pos.x, img_pos.y,
            img_pos.x+file_image.width, img_pos.y+file_image.height)
        return RenderInfo(image, editable_rect, orig_image_scale)
