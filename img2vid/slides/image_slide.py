import tempfile
from PIL import Image as PImage
from PIL import ImageTk
from wand.image import Image as WandImage
from wand.drawing import Drawing as WandDrawing
from wand.color import Color as WandColor

from .slide import Slide
from commons import Rectangle, Point, CustomFontMetric
from commons.image_utils import reverse_orient

FILEPATH = "filepath"
RECT = "rect"
CAPTION = "cap"
CAPTION_ALIGN = "align"
TRANSITION = "trans"

INCH2PIXEL = 72

class ImageSlide(Slide):
    TypeName = "image"

    def __init__(self, filepath,
                 rect=None, caption="", cap_align="",
                 transition=None):
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
        self[TRANSITION] = transition
        self.allow_croppping = True

    def get_exif_orient(self):
        exif = {}
        with WandImage(filename=self.get_filepath()) as image:
            return image.metadata.get("exif:Orientation", None)
        return None

    @classmethod
    def create_from_data(cls, data):
        ob = cls(data[FILEPATH], data[RECT], data[CAPTION], data[CAPTION_ALIGN])
        ob.load_from_data(data)
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

    def get_caption_metric(self, config):
        caption = self.get_caption()
        metric = None
        if caption:
            with WandImage(resolution=config.ppi, width=1, height=1) as canvas:
                with WandDrawing() as context:
                    context.text_alignment = "center"
                    context.font = config.text_font_name
                    context.font_size = int(round(config.text_font_size*config.ppi/INCH2PIXEL))
                    metric = context.get_font_metrics(canvas, self.get_caption(), multiline=True)
                    metric = CustomFontMetric(metric)
                    metric.height = metric.text_height + 2*config.caption_padding
                    metric.top_offset = metric.ascender + config.caption_padding
                    metric.width = metric.text_width + 2*config.caption_padding
        return metric

    def get_caption_image(self, min_width, metric, config, use_pil=False):
        width = int(max(min_width, metric.width))
        height = int(metric.height)

        canvas = WandImage(resolution=config.ppi,
                           width=width, height=height,
                           background=WandColor(config.caption_background_color))
        canvas.format = "png"
        with WandDrawing() as context:
            context.fill_color = WandColor(config.caption_foreground_color)
            context.text_alignment = "center"
            context.font = config.text_font_name
            context.font_size = int(round(config.text_font_size*config.ppi/INCH2PIXEL))
            context.text(
                    x=int(width*0.5),
                    y=int(metric.top_offset), body=self.get_caption())
            context(canvas)
        if not use_pil:
            return canvas
        temporary_file = tempfile.SpooledTemporaryFile()

        canvas.save(file=temporary_file)
        canvas.save(filename="/home/sujoy/Pictures/test.png")
        canvas = None

        image = PImage.open(temporary_file)
        image.load()

        container = PImage.new("RGBA", (width, height))
        container.paste(image, (0, 0))
        temporary_file.close()
        return container

    def crop(self, rect):
        if self.rect:
            rect = rect.copy()
            rect.translate(Point(self.rect.x1, self.rect.y1))
        newob = ImageSlide(self[FILEPATH], rect)
        return newob

    def get_renderable_image(self, config):
        caption = self.get_caption()
        if caption:
            caption_align = self.get_caption_alignment()
            resolution = config.video_resolution

            caption_metric = self.get_caption_metric(config)
            with WandImage(resolution=config.ppi,
                           width=resolution.x, height=resolution.y,
                           background = WandColor(config.video_background_color)) as canvas:
                canvas.units = "pixelsperinch"
                with WandDrawing() as context:
                    if caption_align != "center":
                        allowed_height = resolution.y - caption_metric.height
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

                    caption_image = self.get_caption_image(orig_image.width, caption_metric, config)

                    img_left = int((resolution.x-orig_image.width)*0.5)
                    img_top = int((resolution.y-orig_image.height)*0.5)

                    caption_left = (resolution.x-caption_image.width)*0.5
                    if caption_align == "center":
                        caption_top = (resolution.y-caption_image.height)*0.5
                    else:
                        adjusted_top = (resolution.y-(orig_image.height+caption_image.height))*0.5
                        if caption_align == "top":
                            caption_top = adjusted_top
                            img_top = adjusted_top + caption_image.height
                        elif caption_align == "bottom":
                            img_top = adjusted_top
                            caption_top = adjusted_top + orig_image.height

                    canvas.composite(image=orig_image, left=int(img_left), top=int(img_top))
                    canvas.composite(image=caption_image, left=int(caption_left), top=int(caption_top))
                    context(canvas)

                temporary_file = tempfile.SpooledTemporaryFile()
                canvas.format = "png"
                canvas.save(file=temporary_file)

                image = PImage.open(temporary_file)
                image.load()
                temporary_file.close()
        else:
            image = self.get_image()
        return image