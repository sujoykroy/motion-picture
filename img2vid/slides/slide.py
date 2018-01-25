class Slide(dict):
    IdSeed = 0

    def __init__(self, type):
        super(Slide, self).__init__()
        self["type"] = type
        self.allow_cropping = False
        self.id_num = Slide.IdSeed + 1
        Slide.IdSeed = Slide.IdSeed + 1

    def __eq__(self, other):
        return other and other.id_num == self.id_num