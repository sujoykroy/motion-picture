from PIL import Image, ImageTk

from .slide import Slide
from commons import Rectangle, Point

FILEPATH = "filepath"
RECT = "rect"
CAPTION = "cap"
CAPTION_ALIGN = "align"

class ImageSlide(Slide):
    TypeName = "image"

    def __init__(self, filepath, rect=None, caption=""):
        super(ImageSlide, self).__init__(type=self.TypeName)
        self.set_caption(caption)
        self.set_caption_alignment("")
        self[FILEPATH] = filepath
        if rect:
            if isinstance(rect, dict):
                self[RECT] = rect
                self.rect = Rectangle.create_from_dict(dict)
            else:
                self[RECT] = rect.to_dict()
                self.rect = rect
        else:
            self.rect = None
        if caption:
            self[CAPTION] = caption
        self.allow_croppping = True

    def get_filepath(self):
        return self[FILEPATH]

    def get_caption(self):
        return self[CAPTION]

    def set_caption(self, caption):
        self[CAPTION] = caption

    def set_caption_alignment(self, alignment):
        self[CAPTION_ALIGN] = alignment

    def get_caption_alignment(self):
        align = self[CAPTION_ALIGN]
        if not align:
            align="bottom"
        return align

    def get_image(self, resolution=None):
        image = ImageTk.Image.open(self[FILEPATH])
        if self.rect:
            image = image.crop((self.rect.x1, self.rect.y1, self.rect.x2, self.rect.y2))
        if resolution:
            sx = resolution.x/image.width
            sy = resolution.y/image.height
            sc = min(sx, sy)
            image = image.resize((int(image.width*sc), int(image.height*sc)), resample=True)

            ofx = int((resolution.x-image.width)*0.5)
            ofy = int((resolution.y-image.height)*0.5)

            container = Image.new("RGBA", (resolution.x, resolution.y), "#FFFFFF00")
            container.paste(image, (ofx, ofy))
            image = container
        return image

    def crop(self, rect):
        if self.rect:
            rect = rect.copy()
            rect.translate(Point(self.rect.x1, self.rect.y1))
        newob = ImageSlide(self[FILEPATH], rect)
        return newob