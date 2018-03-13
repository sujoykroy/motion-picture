import re
from ..configs import TextConfig

class Caption:
    def __init__(self, params=None):
        if params is None:
            params = {}
        self._params = params

    @property
    def text(self):
        return self._params.get('text', '')

    @text.setter
    def text(self, value):
        value  = re.sub("[\r\n]$", "", value)
        self._params['text'] = value

    @property
    def valign(self):
        return self._params.get('valign')

    @property
    def font_family(self):
        return self._params.get('font_family', '')

    @font_family.setter
    def font_family(self, value):
        if value is None:
            value = ""
        self._params['font_family'] = value.strip()

    @property
    def font_size(self):
        return self._params.get('font_size', 0)

    @font_size.setter
    def font_size(self, value):
        self._params['font_size'] = value

    @property
    def font_weight(self):
        return self._params.get('font_weight')

    @font_weight.setter
    def font_weight(self, value):
        self._params['font_weight'] = value

    @property
    def font_color(self):
        return self._params.get('font_color', '')

    @font_color.setter
    def font_color(self, value):
        self._params['font_color'] = value

    @property
    def font_style(self):
        return self._params.get('font_style', '')

    @font_style.setter
    def font_style(self, value):
        self._params['font_style'] = value

    @property
    def back_color(self):
        return self._params.get('back_color', '')

    @back_color.setter
    def back_color(self, value):
        self._params['back_color'] = value

    def get_json(self):
        return dict(self._params)

    @classmethod
    def create_from_json(cls, data):
        newob = cls(data)
        return newob
