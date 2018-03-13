import re

import wand.image
import wand.drawing
import wand.version

from .font_metric import FontMetric

FONT_REPLACERS = "(?i)(" +\
                 "|".join(wand.drawing.STYLE_TYPES + ('bold',)) + \
                 ")"

class TextAnalyser:
    @staticmethod
    def get_font_families():
        fonts = wand.version.fonts()
        return fonts
        for i in range(len(fonts)):
            font = fonts[i]
            font = re.sub(FONT_REPLACERS, "", font)
            font = re.sub("(--|-$)", "", font)
            fonts[i] = font
        return sorted(list(set(fonts)))

    @staticmethod
    def get_font_styles():
        return wand.drawing.STYLE_TYPES

    @staticmethod
    def get_font_metric(caption, text_config):
        metric = None
        with wand.image.Image(resolution=text_config.ppi, width=1, height=1) as canvas:
            with wand.drawing.Drawing() as context:
                context.text_alignment = "center"
                if caption.font_family:
                    context.font = caption.font_family
                else:
                    context.font = text_config.font_name
                if caption.font_size:
                   context.font_size = \
                        text_config.get_font_point_to_pixel(caption.font_size)
                else:
                    context.font_size = text_config.font_pixel_size
                metric = context.get_font_metrics(canvas, caption.text, multiline=True)
                metric = FontMetric(metric)
                metric.height = metric.text_height + 2*text_config.padding
                metric.top_offset = metric.ascender + text_config.padding
                metric.width = metric.text_width + 2*text_config.padding
        return metric
