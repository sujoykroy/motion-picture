class CustomFontMetric:
    def __init__(self, other):
        self.text_height = other.text_height
        self.text_width = other.text_width
        self.height = other.text_height
        self.width = other.text_width
        self.ascender = other.ascender
        self.descender = other.descender
        self.x = other.x
        self.y = other.y
        self.x1 = other.x1
        self.x2 = other.x2
        self.y1 = other.y1
        self.y2 = other.y2
        self.character_height = other.character_height
        self.character_width = other.character_width
        self.maximum_horizontal_advance = other.maximum_horizontal_advance