import wand.image
import wand.drawing
import wand.color

from ..analysers import TextAnalyser

class CaptionRenderer:
    @classmethod
    def caption2image(cls, caption, min_width, text_config, wand_image=False):
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
                x=int(width*0.5), y=int(font_metric.top_offset), body=caption.text)
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
