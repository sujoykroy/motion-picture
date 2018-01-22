class Slide(dict):
    def __init__(self, type):
        super(Slide, self).__init__()
        self["type"] = type
        self.allow_cropping = False
