from .slide import Slide

class TextSlide(Slide):
    TypeName = "text"

    def __init__(self, text):
        super(TextSlide, self).__init__(type=self.TypeName)
        self["text"] = text