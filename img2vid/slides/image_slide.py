from .slide import Slide
from ..geom import Point, Rectangle
from .caption import Caption

class ImageSlide(Slide):
    TYPE_NAME = "image"
    KEY_FILEPATH = "filepath"
    KEY_RECT = "rect"
    KEY_CAPTIONS = "caps"

    CAP_ALIGN_TOP = "top"
    CAP_ALIGN_CENTER = "center"
    CAP_ALIGN_BOTTOM = "bottom"
    CAP_ALIGNMENTS = [CAP_ALIGN_TOP, CAP_ALIGN_CENTER, CAP_ALIGN_BOTTOM]

    def __init__(self, filepath, rect=None):
        super().__init__()
        self._filepath = filepath
        self._rect = rect
        self._captions = {}

        for valign in self.CAP_ALIGNMENTS:
            self._captions[valign] = Caption(
                {'valign': valign, 'text': ''})

    def get_caption(self, valign):
        return self._captions[valign]

    def set_caption(self, caption):
        self._captions[caption.valign] = caption

    @property
    def active_captions(self):
        caps = []
        for cap in self._captions.values():
            if cap.text:
                caps.append(cap)
        return caps

    @property
    def has_caption(self):
        for cap in self._captions.values():
            if cap.text:
                return True
        return False

    @property
    def crop_allowed(self):
        return True

    @property
    def filepath(self):
        return self._filepath

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
        data[self.KEY_CAPTIONS] = []
        for caption in self._captions.values():
            if caption.text:
                data[self.KEY_CAPTIONS].append(caption.get_json())
        return data

    @classmethod
    def create_from_json(cls, data):
        newob = cls(filepath=data.get(cls.KEY_FILEPATH),
                    rect=Rectangle.create_from_json(data.get(cls.KEY_RECT)))
        captions_data = data.get(cls.KEY_CAPTIONS, [])
        for caption_data in captions_data:
            caption = Caption.create_from_json(caption_data)
            newob.set_caption(caption)
        newob.load_effects_from_json(data)
        return newob
