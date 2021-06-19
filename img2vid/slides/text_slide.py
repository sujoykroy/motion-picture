from ..effects import NumberParamChange
from .slide import Slide
from .caption import Caption


class TextSlide(Slide):
    TYPE_NAME = "text"
    KEY_CAPTION = "cap"
    KEY_WIDTH_FRAC = "width_frac"

    CONSTRUCTOR_KEYS = Slide.CONSTRUCTOR_KEYS + [
        KEY_CAPTION, KEY_WIDTH_FRAC]

    def __init__(self, cap=None, **kwargs):
        super().__init__(**kwargs)
        if not cap:
            cap = Caption()
        self._caption = cap
        self.width_frac = kwargs.get(self.KEY_WIDTH_FRAC)

    @property
    def cap(self):
        return self._caption

    @property
    def active_captions(self):
        return [self._caption]

    @property
    def vtext_frac(self):
        return self._caption.vfrac

    @vtext_frac.setter
    def vtext_frac(self, value):
        self._caption.vfrac = value

    @property
    def caption(self):
        return self._caption

    def get_json(self):
        data = super().get_json()
        data[self.KEY_CAPTION] = self._caption.get_json()
        return data

    @classmethod
    def create_from_json(cls, data):
        caption = data.pop(cls.KEY_CAPTION, None)
        if caption:
            caption = Caption.create_from_json(caption)
        newob = super().create_from_json({
            'cap':caption, **data
        })
        return newob

    @classmethod
    def new_with_text(cls, text):
        caption = Caption({'text': text})
        newob = cls(caption)
        return newob
