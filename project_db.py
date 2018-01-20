import os

class Slide(dict):
    def __init__(self, type):
        super(Slide, self).__init__()
        self["type"] = type

class TextSlide(Slide):
    TypeName = "text"

    def __init__(self, text):
        super(TextSlide, self).__init__(type=self.TypeName)
        self["text"] = text

class ImageSlide(Slide):
    TypeName = "image"

    def __init__(self, filepath, rect=None, caption=None):
        super(ImageSlide, self).__init__(type=self.TypeName)
        self["filepath"] = filepath
        if rect:
            self["rect"] = rect
        if caption:
            self["caption"] = caption

class ProjectDb:
    def __init__(self, filepath):
        self.filepath = filepath
        if os.path.isfile(self.filepath):
            with open(self.filepath, "r") as f:
                self.data = json.load(f)
        else:
            self.data = dict(items=[])
        self.items = self.data["items"]

    def save(self):
        if not self.filepath:
            return
        with open(self.filepath, "w") as f:
            json.dump(f)

    def add_slide(self, slide):
        self.items.append(slide)
