from .slide import Slide

class TextSlide(Slide):
    TypeName = "text"

    def __init__(self, text):
        super(TextSlide, self).__init__(type=self.TypeName)
        self.set_text(text)

    def set_text(self, text):
        self["text"] = text

    def get_text(self):
        return self["text"]