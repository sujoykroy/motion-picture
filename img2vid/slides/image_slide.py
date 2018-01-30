import tempfile
from PIL import Image as tkImage
from PIL import ImageTk
from wand.image import Image as WandImage
from wand.drawing import Drawing as WandDrawing
from wand.color import Color as WandColor

from .slide import Slide
from commons import Rectangle, Point
from commons.image_utils import reverse_orient

FILEPATH = "filepath"
RECT = "rect"
CAPTION = "cap"
CAPTION_ALIGN = "align"

class ImageSlide(Slide):
    TypeName = "image"

    def __init__(self, filepath, rect=None, caption="", cap_align=""):
        super(ImageSlide, self).__init__(type=self.TypeName)
        self.set_caption(caption)
        self.set_caption_alignment(cap_align)
        self[FILEPATH] = filepath
        if rect:
            if isinstance(rect, dict):
                self[RECT] = rect
                self.rect = Rectangle.create_from_dict(rect)
            else:
                self[RECT] = rect.to_dict()
                self.rect = rect
        else:
            self[RECT] = None
            self.rect = None
        self.allow_croppping = True

    def get_exif_orient(self):
        exif = {}
        with WandImage(filename=self.get_filepath()) as image:
            return image.metadata.get("exif:Orientation", None)
        return None

    @classmethod
    def create_from_data(cls, data):
        ob = cls(data[FILEPATH], data[RECT], data[CAPTION], data[CAPTION_ALIGN])
        return ob

    def get_filepath(self):
        return self[FILEPATH]

    def get_caption(self):
        return self[CAPTION]

    def set_caption(self, caption):
        self[CAPTION] = caption.strip()

    def set_caption_alignment(self, alignment):
        self[CAPTION_ALIGN] = alignment

    def get_caption_alignment(self):
        align = self[CAPTION_ALIGN]
        if not align:
            align="bottom"
        return align

    def get_image(self):
        image = ImageTk.Image.open(self[FILEPATH])
        image = reverse_orient(image, exif_orient=self.get_exif_orient())
        if self.rect:
            image = image.crop((self.rect.x1, self.rect.y1, self.rect.x2, self.rect.y2))
        return image

    def get_caption_size(self, config):
        caption = self.get_caption()
        size = None
        if caption:
            with WandImage(resolution=config.ppi, width=1, height=1) as canvas:
                with WandDrawing() as context:
                    context.text_alignment = "center"
                    context.font = config.text_font_name
                    context.font_size = int(round(config.text_font_size*config.ppi/72))
                    metric = context.get_font_metrics(canvas, self.get_caption(), multiline=True)
                    size = Point(metric.text_width, metric.text_height)
        return size

    def crop(self, rect):
        if self.rect:
            rect = rect.copy()
            rect.translate(Point(self.rect.x1, self.rect.y1))
        newob = ImageSlide(self[FILEPATH], rect)
        return newob

    def get_renderable_image(self, resolution, config):
        caption = self.get_caption()
        caption_align = self.get_caption_alignment()
        if caption:
            with WandImage(resolution=config.ppi,
                           width=resolution.x, height=resolution.y,
                           background = WandColor(config.video_background_color)) as canvas:
                canvas.units = "pixelsperinch"
                with WandDrawing() as context:
                    context.text_alignment = "center"
                    context.font = config.text_font_name
                    context.font_size = int(round(config.text_font_size*config.ppi/72))
                    metric = context.get_font_metrics(canvas, self.get_caption(), multiline=True)

                    if caption_align != "center":
                        allowed_height = resolution.y - metric.text_height
                    else:
                        allowed_height = resolution.y

                    orig_image = WandImage(filename=self[FILEPATH])
                    orig_image = reverse_orient(orig_image, exif_orient=self.get_exif_orient())
                    if self.rect:
                        orig_image.crop(
                            int(self.rect.x1), int(self.rect.y1),
                            int(self.rect.x2), int(self.rect.y2))
                    scale = min(resolution.x/orig_image.width, allowed_height/orig_image.height)
                    orig_image.resize(width=int(orig_image.width*scale),
                                      height=int(orig_image.height*scale))

                    img_left = int((resolution.x-orig_image.width)*0.5)
                    img_top = int((resolution.y-orig_image.height)*0.5)

                    if caption_align == "center":
                        text_top = (resolution.y-metric.text_height)*0.5
                    else:
                        adjusted_top = (resolution.y-(orig_image.height+metric.text_height))*0.5
                        if caption_align == "top":
                            text_top = adjusted_top
                            img_top = adjusted_top + metric.text_height
                        elif caption_align == "bottom":
                            img_top = adjusted_top
                            text_top = adjusted_top + orig_image.height
                    text_top += metric.character_height

                    canvas.composite(image=orig_image, left=int(img_left), top=int(img_top))

                    context.fill_color = WandColor(config.caption_background_color)
                    text_box_width = max(orig_image.width, metric.text_width)
                    context.rectangle(
                        left=(resolution.x-text_box_width)*0.5,
                        top=int(text_top-metric.character_height),
                        width = int(text_box_width), height = int(metric.text_height))

                    context.fill_color = WandColor(config.caption_foreground_color)
                    context.text(
                        x=int(resolution.x*.5),
                        y=int(text_top+metric.descender), body=caption)
                    context(canvas)

                temporary_file = tempfile.SpooledTemporaryFile()
                canvas.format = "png"
                canvas.save(file=temporary_file)

                image = tkImage.open(temporary_file)
                image.load()
                temporary_file.close()
        else:
            image = self.get_image()
        return image