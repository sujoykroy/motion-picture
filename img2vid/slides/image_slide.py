from .slide import Slide
from ..geom import Point, Rectangle

class ImageSlide(Slide):
    TYPE_NAME = "image"
    KEY_FILEPATH = "filepath"
    KEY_RECT = "rect"
    KEY_CAPTION = "cap"
    KEY_CAP_ALIGN = "align"

    CAP_ALIGN_TOP = "top"
    CAP_ALIGN_CENTER = "center"
    CAP_ALIGN_BOTTOM = "bottom"
    CAP_ALIGNMENTS = [CAP_ALIGN_TOP, CAP_ALIGN_CENTER, CAP_ALIGN_BOTTOM]

    def __init__(self, filepath, rect=None, caption="", cap_align=""):
        super().__init__()
        self._caption = caption.strip()
        if not cap_align:
            cap_align = "bottom"
        self._cap_align = cap_align
        self._filepath = filepath
        self._rect = rect

    @property
    def crop_allowed(self):
        return True

    @property
    def text(self):
        return self._caption

    @text.setter
    def text(self, value):
        self._caption = value.strip()

    @property
    def caption(self):
        return self._caption

    @property
    def filepath(self):
        return self._filepath

    @property
    def cap_align(self):
        return self._cap_align

    @cap_align.setter
    def cap_align(self, value):
        self._cap_align = value

    @property
    def rect(self):
        return self._rect

    def crop(self, rect):
        if self._rect:
            rect = rect.copy()
            rect.translate(Point(self._rect.x1, self._rect.y1))
        newob = ImageSlide(self._filepath, rect)
        return newob

    def get_json(self):
        data = super().get_json()
        data[self.KEY_FILEPATH] = self._filepath
        if self._rect:
            data[self.KEY_RECT] = self._rect.get_json()
        data[self.KEY_CAPTION] = self._caption
        data[self.KEY_CAP_ALIGN] = self._cap_align
        return data

    @classmethod
    def create_from_json(cls, data):
        newob = cls(filepath=data.get(cls.KEY_FILEPATH),
                    rect=Rectangle.create_from_json(data.get(cls.KEY_RECT)),
                    caption=data.get(cls.KEY_CAPTION),
                    cap_align=data.get(cls.KEY_CAP_ALIGN))
        newob.load_effects_from_json(data)
        return newob
