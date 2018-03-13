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
