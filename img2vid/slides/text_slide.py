from ..effects import NumberParamChange
from .slide import Slide
from .caption import Caption


class TextSlide(Slide):
    TYPE_NAME = "text"
    KEY_CAPTION = "cap"

    def __init__(self, caption=None):
        super().__init__()
        if not caption:
            caption = Caption()
        self._caption = caption

        self.add_effect(NumberParamChange, {
            'param_name': 'vtext_frac',
            'value_start': 0,
            'value_end': 1,
            'scale': 3
        })

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
        caption = Caption.create_from_json(data.get(cls.KEY_CAPTION))
        newob = cls(caption=caption)
        newob.load_effects_from_json(data)
        return newob

    @classmethod
    def new_with_text(cls, text):
        caption = Caption({'text': text})
        newob = cls(caption)
        return newob
