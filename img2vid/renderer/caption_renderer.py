import subprocess
import tempfile


import wand.image
import wand.drawing
import wand.color

from ..analysers import TextAnalyser
from ..utils import ImageUtils
from ..geom.rectangle import Rectangle
from ..geom.point import Point
from ..slides.image_slide import ImageSlide
from .vector_renderer import VectorRenderer
from ..configs.vector_config import VectorConfig


class CaptionRenderer:
    @classmethod
    def create_focuser_image(cls, caption, caption_image, cap_pos, wand_image=False):
        focuser = caption.focuser
        halign = caption.halign
        valign = caption.valign
        if focuser.get('type') == 'anchored_rect':
            padding = 4 * caption.padding
            spread = focuser.get('spread', 5)
            focuser_shape = Rectangle(
                cap_pos.x, cap_pos.y,
                cap_pos.x + caption_image.width,
                cap_pos.y + caption_image.height
            )
            if halign == ImageSlide.CAP_ALIGN_LEFT:
                focuser_shape.x1 = cap_pos.x + caption_image.width + padding
                focuser_shape.x2 = focuser_shape.x1 + spread
            elif halign == ImageSlide.CAP_ALIGN_RIGHT:
                focuser_shape.x2 = cap_pos.x - padding
                focuser_shape.x1 = focuser_shape.x2 - spread

            if valign == ImageSlide.CAP_ALIGN_TOP:
                if halign ==  ImageSlide.CAP_ALIGN_CENTER:
                    focuser_shape.y1 = cap_pos.y + caption_image.height + padding
                    focuser_shape.y2 = focuser_shape.y1 + spread
            else:
                if halign ==  ImageSlide.CAP_ALIGN_CENTER:
                    focuser_shape.y2 = cap_pos.y - padding
                    focuser_shape.y1 = focuser_shape.y2 - spread

            draw_rect = Rectangle(
                0, 0,
                focuser_shape.width, focuser_shape.height
            )
            vector_config = VectorConfig(fill_color=caption.focuser_fill_color)
            image = VectorRenderer.create_image(draw_rect, vector_config, wand_image=wand_image)
            return image, Point(focuser_shape.x1, focuser_shape.y1)

    @classmethod
    def caption2image(cls, caption, max_width, text_config, wand_image=False):
        vtext = caption.visible_text
        if not vtext:
            return None

        dest_image_file = tempfile.NamedTemporaryFile(suffix='.png')
        filename = dest_image_file.name
        args = [
            'convert'
        ]
        back_color = caption.back_color  or text_config.back_color
        args.extend(['-channel', "RGBA"])
        args.extend(['-background', back_color])
        args.extend(['-gravity', "center"])
        args.extend(['-trim'])
        args.extend(['-size', str(max_width)])

        if caption.font_family:
            font_family = caption.font_family
        else:
            font_family = text_config.font_name

        if caption.font_size:
            font_size = \
                text_config.get_font_point_to_pixel(int(caption.font_size) * text_config.scale)
        else:
            font_size = text_config.font_pixel_size

        if caption.font_color:
            font_color = caption.font_color
        else:
            font_color = text_config.font_color
        text = '''
        <span
            font_family="{font_family}"
            size="{font_size}"
            foreground="{font_color}">{text}</span>
        '''.format(
            font_family=font_family,
            font_size=int(font_size) * 1000,
            font_color=font_color,
            font_style=caption.font_style,
            font_weight=caption.font_weight,
            text=vtext
        )
        args.append('pango:' + text)
        args.append(filename)
        subprocess.call(args)
        image = ImageUtils.fetch_image(filename, crop=None, wand_image=wand_image)
        dest_image_file.close()

        padding = caption.padding
        canvas = ImageUtils.create_blank(
            image.width + 2 * padding,
            image.height + 2 * padding,
            back_color
        )
        canvas = ImageUtils.pil2wand(canvas)
        with wand.drawing.Drawing() as context:
            canvas.composite(image=image, left=padding, top=padding)

        if wand_image:
            return canvas
        return ImageUtils.wand2pil(canvas)

'''
    @classmethod
    def caption2image_old(cls, caption, min_width, text_config, wand_image=False):
        font_metric = TextAnalyser.get_font_metric(caption, text_config)
        width = int(max(min_width, font_metric.width))
        height = int(font_metric.height)
        back_color = caption.back_color or text_config.back_color

        canvas = wand.image.Image(
            resolution=text_config.ppi,
            width=width, height=height,
            background=wand.color.Color(back_color))
        canvas.format = "png"

        with wand.drawing.Drawing() as context:
            cls.apply_caption(context, caption, text_config)

            context.text_alignment = "center"
            context.text(
                x=int(width*0.5), y=int(font_metric.top_offset),
                body=caption.visible_text
            )
            context(canvas)
            if wand_image:
                image = canvas
            else:
                image = cls.wand2pil(canvas)
        return image

    @staticmethod
    def apply_caption(context, caption, text_config):
        if caption.font_family:
            context.font_family = caption.font_family
        else:
            context.font = text_config.font_name

        if caption.font_size:
            context.font_size = \
                text_config.get_font_point_to_pixel(caption.font_size)
        else:
            context.font_size = text_config.font_pixel_size
        context.font_size *= text_config.scale

        if caption.font_color:
            context.fill_color = wand.color.Color(caption.font_color)
        else:
            context.fill_color = wand.color.Color(text_config.font_color)

        if caption.font_style:
            context.font_style = caption.font_style
        if caption.font_weight:
            context.font_weight = caption.font_weight
'''
