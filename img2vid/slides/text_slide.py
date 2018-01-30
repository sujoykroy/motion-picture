import tempfile
from PIL import Image as tkImage

from wand.image import Image as WandImage
from wand.drawing import Drawing as WandDrawing
from wand.color import Color as WandColor

from .slide import Slide

class TextSlide(Slide):
    TypeName = "text"

    def __init__(self, text):
        super(TextSlide, self).__init__(type=self.TypeName)
        self.set_text(text)

    @classmethod
    def create_from_data(cls, data):
        ob = cls(data["text"])
        return ob

    def set_text(self, text):
        self["text"] = text.strip()

    def get_text(self):
        return self["text"]

    def get_renderable_image(self, config):
        resolution = config.video_resolution
        with WandImage(resolution=config.ppi, width=resolution.x, height=resolution.y,
                       background=WandColor(config.text_background_color)) as canvas:
            canvas.units = "pixelsperinch"
            with WandDrawing() as context:
                context.font = config.text_font_name
                context.fill_color = WandColor(config.text_foreground_color)
                context.font_size = int(round(config.text_font_size*config.ppi/72))
                context.gravity = "center"
                context.text(x=0, y=0, body=self.get_text())
                context(canvas)

            temporary_file = tempfile.SpooledTemporaryFile()
            canvas.format = "png"
            canvas.save(file=temporary_file)

            image = tkImage.open(temporary_file)
            image.load()
            temporary_file.close()
        return image