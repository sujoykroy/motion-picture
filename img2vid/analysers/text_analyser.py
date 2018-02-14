import wand.image
import wand.drawing

from .font_metric import FontMetric


class TextAnalyser:
    @staticmethod
    def get_font_metric(text, text_config):
        metric = None
        with wand.image.Image(resolution=text_config.ppi, width=1, height=1) as canvas:
            with wand.drawing.Drawing() as context:
                context.text_alignment = "center"
                context.font = text_config.font_name
                context.font_size = int(round(
                    text_config.font_size*text_config.ppi/text_config.INCH2PIXEL))
                metric = context.get_font_metrics(canvas, text, multiline=True)
                metric = FontMetric(metric)
                metric.height = metric.text_height + 2*text_config.padding
                metric.top_offset = metric.ascender + text_config.padding
                metric.width = metric.text_width + 2*text_config.padding
        return metric
