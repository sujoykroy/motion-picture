from PIL import Image, ImageTk

from .slide import Slide

class ImageSlide(Slide):
    TypeName = "image"

    def __init__(self, filepath, rect=None, caption=None):
        super(ImageSlide, self).__init__(type=self.TypeName)
        self["filepath"] = filepath
        if rect:
            self["rect"] = rect
        if caption:
            self["caption"] = caption

    def get_image(self):
        image = ImageTk.Image.open(self["filepath"])
        return image