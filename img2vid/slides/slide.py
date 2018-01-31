FILTERS = "flt"

class Slide(dict):
    IdSeed = 0
    FILTER_FADE_IN = 0
    FILTER_FADE_OUT = 1

    @classmethod
    def get_filter_types(cls):
        return {cls.FILTER_FADE_IN: "fade-in" , cls.FILTER_FADE_OUT: "fade-out"}

    def __init__(self, type):
        super(Slide, self).__init__()
        self["type"] = type
        self.allow_cropping = False
        self.id_num = Slide.IdSeed + 1
        self.filters = self[FILTERS] = []
        Slide.IdSeed = Slide.IdSeed + 1

    def load_from_data(self, data):
        if FILTERS in data:
            self.set_filters(data[FILTERS])

    def set_filters(self, filters):
        del self.filters[:]
        for filter in filters:
            self.filters.append(filter)

    def __hash__(self):
        return self.id_num

    def __eq__(self, other):
        return other and other.id_num == self.id_num