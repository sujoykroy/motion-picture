from .slide import Slide

class TextSlide(Slide):
    TYPE_NAME = "text"
    KEY_TEXT = "text"

    def __init__(self, text):
        super().__init__()
        self._text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    def get_json(self):
        data = super().get_json()
        data[self.KEY_TEXT] = self._text
        return data

    @classmethod
    def create_from_json(cls, data):
        newob = cls(text=data.get(cls.KEY_TEXT))
        newob.load_effects_from_json(data)
        return newob
