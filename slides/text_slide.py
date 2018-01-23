import tempfile
from PIL import Image, ImageDraw, ImageFont

from wand.image import Image as WandImage
from wand.drawing import Drawing as WandDrawing
from wand.color import Color as WandColor

from .slide import Slide


class TextSlide(Slide):
    TypeName = "text"

    def __init__(self, text):
        super(TextSlide, self).__init__(type=self.TypeName)
        self.set_text(text)

    def set_text(self, text):
        self["text"] = text

    def get_text(self):
        return self["text"]

    def get_image(self, resolution, config):
        canvas = WandImage(
                        width=resolution.x, height=resolution.y,
                        background=WandColor(config.text_background_color))
        with WandDrawing() as context:
            context.fill_color = WandColor(config.text_foreground_color)
            context.font_size = int(round(config.text_font_size*2))
            context.gravity = "center"
            context.text(x=0, y=0, body=self.get_text())
            context(canvas)
        temporary_file = tempfile.NamedTemporaryFile()
        canvas.format = "png"
        canvas.save(file=temporary_file)
        image = Image.open(temporary_file)
        image.load()
        temporary_file.close()
        return image

    def get_image1(self, resolution, config):
        image = Image.new("RGBA", (resolution.x, resolution.y), config.text_background_color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype('{}'.format(config.text_font_name), config.text_font_size)
        except:
            font = None
        text_width, text_height = draw.textsize(self.get_text())
        draw.text(
            ((resolution.x-text_width)*0.5, (resolution.y-text_height)*0.5),
            self.get_text(), fill=config.text_foreground_color)
        return image