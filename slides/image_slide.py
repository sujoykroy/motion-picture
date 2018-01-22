from PIL import Image, ImageTk

from .slide import Slide
from commons import Rectangle, Point

class ImageSlide(Slide):
    TypeName = "image"

    def __init__(self, filepath, rect=None, caption=""):
        super(ImageSlide, self).__init__(type=self.TypeName)
        self.set_caption(caption)
        self.set_caption_alignment("")
        self["filepath"] = filepath
        if rect:
            if isinstance(rect, dict):
                self["rect"] = rect
                self.rect = Rectangle.create_from_dict(dict)
            else:
                self["rect"] = rect.to_dict()
                self.rect = rect
        else:
            self.rect = None
        if caption:
            self["caption"] = caption
        self.allow_croppping = True

    def get_caption(self):
        return self["cap"]

    def set_caption(self, caption):
        self["cap"] = caption

    def set_caption_alignment(self, alignment):
        self["align"] = alignment

    def get_caption_alignment(self):
        align = self["align"]
        if not align:
            align="bottom"
        return align

    def get_image(self):
        image = ImageTk.Image.open(self["filepath"])
        if self.rect:
            image = image.crop((self.rect.x1, self.rect.y1, self.rect.x2, self.rect.y2))
        return image

    def crop(self, rect):
        if self.rect:
            rect = rect.copy()
            rect.translate(Point(self.rect.x1, self.rect.y1))
        newob = ImageSlide(self["filepath"], rect)
        return newob