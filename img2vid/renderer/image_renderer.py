import tempfile

import PIL
import PIL.Image

import wand.image
import wand.drawing
import wand.color

import numpy

from ..geom import Rectangle, Point
from ..slides import ImageSlide
from ..analysers import ImageAnalyser, TextAnalyser
from .render_info import RenderInfo

PIXEL_PER_INCH = "pixelsperinch"

class ImageRenderer:
    EXIF_TO_RENDERER_ORIENTATION = {
        '2' : PIL.Image.FLIP_LEFT_RIGHT,
        '3' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.FLIP_TOP_BOTTOM],
        '4' : PIL.Image.FLIP_TOP_BOTTOM,
        '5' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.ROTATE_270],
        '6' : PIL.Image.ROTATE_270,
        '7' : [PIL.Image.FLIP_LEFT_RIGHT, PIL.Image.ROTATE_90],
        '8' : PIL.Image.ROTATE_90
    }

    @classmethod
    def build_text_slide(cls, slide, screen_config, text_config):
        bg_color = wand.color.Color(text_config.back_color)
        with wand.image.Image(resolution=text_config.ppi,
                              width=screen_config.width,
                              height=screen_config.height,
                              background=bg_color) as canvas:
            canvas.units = PIXEL_PER_INCH
            with wand.drawing.Drawing() as context:
                context.font = text_config.font_name
                context.fill_color = wand.color.Color(text_config.font_color)
                context.font_size = text_config.font_pixel_size
                context.gravity = "center"
                context.text(x=0, y=0, body=slide.text)
                context(canvas)
                image = cls.wand2pil(canvas)
        return RenderInfo(image)

    @classmethod
    def build_image_slide(cls, slide, screen_config, image_config):
        if not slide.caption:
            image = cls.fetch_image(
                filepath=slide.filepath, crop=slide.rect)
            return RenderInfo(image)

        caption_metric = TextAnalyser.get_font_metric(slide.caption, image_config)
        with wand.image.Image(resolution=image_config.ppi,
                              width=screen_config.width,
                              height=screen_config.height) as canvas:
            canvas.units = PIXEL_PER_INCH
            with wand.drawing.Drawing() as context:
                file_image = cls.fetch_image(
                    filepath=slide.filepath, crop=slide.rect, wand_image=True)

                if slide.cap_align != ImageSlide.CAP_ALIGN_CENTER:
                    allowed_height = screen_config.height - caption_metric.height
                else:
                    allowed_height = screen_config.height

                fitted_image = cls.fit_inside(
                    file_image, screen_config.width, allowed_height)
                orig_image_scale = fitted_image.width/file_image.width
                file_image = fitted_image
                del fitted_image

                cap_image = cls.text2image(
                    text=slide.caption, min_width=file_image.width,
                    text_config=image_config, wand_image=True)

                img_pos = Point(
                    int((screen_config.width-file_image.width)*0.5),
                    int((screen_config.height-file_image.height)*0.5))

                cap_pos = Point(
                    (screen_config.width-cap_image.width)*0.5, 0)
                if slide.cap_align == ImageSlide.CAP_ALIGN_CENTER:
                    cap_pos.y = (screen_config.height-cap_image.height)*0.5
                else:
                    adjusted_top = \
                        (screen_config.height-(file_image.height+cap_image.height))*0.5
                    if slide.cap_align == ImageSlide.CAP_ALIGN_TOP:
                        cap_pos.y = adjusted_top
                        img_pos.y = adjusted_top + cap_image.height
                    elif slide.cap_align == ImageSlide.CAP_ALIGN_BOTTOM:
                        img_pos.y = adjusted_top
                        cap_pos.y = adjusted_top + file_image.height

                img_pos.x = int(img_pos.x)
                img_pos.y = int(img_pos.y)
                cap_pos.x = int(cap_pos.x)
                cap_pos.y = int(cap_pos.y)

                canvas.composite(image=file_image, left=img_pos.x, top=img_pos.y)
                canvas.composite(image=cap_image, left=cap_pos.x, top=cap_pos.y)
                context(canvas)
                image = cls.wand2pil(canvas)
        editable_rect = Rectangle(
            img_pos.x, img_pos.y,
            img_pos.x+file_image.width, img_pos.y+file_image.height)
        return RenderInfo(image, editable_rect, orig_image_scale)

    @classmethod
    def fetch_image(cls, filepath, crop, wand_image=False):
        exif = ImageAnalyser.get_exif(filepath)
        exif_orient = exif.get(ImageAnalyser.KEY_EXIF_ORIENTATION)

        if wand_image:
            image = wand.image.Image(filename=filepath)
            image = cls.reverse_orient(image, exif_orient=exif_orient)
            if crop:
                image.crop(int(crop.x1), int(crop.y1),
                           int(crop.x2), int(crop.y2))
        else:
            image = PIL.Image.open(filepath).convert("RGBA")
            image = cls.reverse_orient(image, exif_orient=exif_orient)
            if crop:
                image = image.crop((crop.x1, crop.y1, crop.x2, crop.y2))
        return image

    @classmethod
    def text2image(cls, text, min_width, text_config, wand_image=False):
        font_metric = TextAnalyser.get_font_metric(text, text_config)
        width = int(max(min_width, font_metric.width))
        height = int(font_metric.height)

        canvas = wand.image.Image(
            resolution=text_config.ppi,
            width=width, height=height,
            background=wand.color.Color(text_config.back_color))
        canvas.format = "png"
        with wand.drawing.Drawing() as context:
            context.fill_color = wand.color.Color(text_config.font_color)
            context.text_alignment = "center"
            context.font = text_config.font_name
            context.font_size = text_config.font_pixel_size
            context.text(
                x=int(width*0.5), y=int(font_metric.top_offset), body=text)
            context(canvas)
            if wand_image:
                image = canvas
            else:
                image = cls.wand2pil(canvas)
        return image

    @classmethod
    def fit_inside(cls, image, width, height):
        scale_x = width/image.width
        scale_y = height/image.height
        scale = min(scale_x, scale_y)
        image = cls.resize(
            image,
            width=int(image.width*scale),
            height=int(image.height*scale))
        return image

    @classmethod
    def fit_full(cls, image, width, height):
        """"This will make the image fit given width and height.
        To keep aspcet ratio, it will automactically cut of some boder zones."""

        max_scale = max(width/image.width, height/image.height)
        image = cls.same_scale(image, max_scale)
        rect = Rectangle()
        rect.set_cxy_wh(
            image.width/2, image.height/2,
            width, height)
        return cls.crop(image, rect)

    @classmethod
    def same_scale(cls, image, scale):
        return cls.resize(
            image, int(image.width*scale), int(image.height*scale))

    @staticmethod
    def resize(image, width, height):
        if isinstance(image, wand.image.Image):
            image = wand.image.Image(image=image)
            image.resize(width, height)
        else:
            image = image.resize((width, height), resample=True)
        return image

    @classmethod
    def crop(cls, image, rect):
        if isinstance(image, wand.image.Image):
            image.crop(
                int(rect.x1), int(rect.y1), int(rect.x2), int(rect.y2))
        else:
            image = image.crop((rect.x1, rect.y1, rect.x2, rect.y2))
        return image

    @staticmethod
    def wand2pil(wand_image):
        wand_image.format = "png"
        temporary_file = tempfile.SpooledTemporaryFile()

        wand_image.save(file=temporary_file)

        pil_image = PIL.Image.open(temporary_file)
        pil_image.load()
        temporary_file.close()

        return pil_image.convert("RGBA")

    @classmethod
    def reverse_orient(cls, image, exif_orient=None, renderer_orient=None):
        if exif_orient:
            renderer_orient = \
                cls.EXIF_TO_RENDERER_ORIENTATION.get(exif_orient, None)
        if not renderer_orient:
            return image
        if isinstance(renderer_orient, list):
            for orient in renderer_orient:
                image = cls.reverse_orient(image, renderer_orient=orient)
            return image
        if not hasattr(image, "flop"):#for PIL Image
            image = image.transpose(renderer_orient)
        else:
            image = wand.image.Image(image)
            if renderer_orient == PIL.Image.FLIP_LEFT_RIGHT:
                image.flop()
            elif renderer_orient == PIL.Image.FLIP_TOP_BOTTOM:
                image.flip()
            elif renderer_orient == PIL.Image.ROTATE_90:
                image.rotate(-90)
            elif renderer_orient == PIL.Image.ROTATE_270:
                image.rotate(90)
        return image

    @staticmethod
    def create_blank(width, height, fill_color):
        image = PIL.Image.new("RGBA", (int(width), int(height)), fill_color)
        return image

    @staticmethod
    def set_alpha(image, alpha):
        image = image.convert("RGBA")
        img_buffer = numpy.array(image, dtype=numpy.uint8)
        img_buffer[:, :, 3] = img_buffer[:, :, 3]*alpha
        img_buffer.dtype = numpy.uint8
        image = PIL.Image.fromarray(img_buffer)
        return image
