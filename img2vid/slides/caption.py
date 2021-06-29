import re
from ..configs import TextConfig

class Caption:
    CAP_ALIGN_TOP = "top"
    CAP_ALIGN_CENTER = "center"
    CAP_ALIGN_BOTTOM = "bottom"
    CAP_ALIGN_LEFT = "left"
    CAP_ALIGN_RIGHT = "right"

    CAP_POS_WEIGHTS = {
        CAP_ALIGN_TOP: 0,
        CAP_ALIGN_CENTER: 1,
        CAP_ALIGN_BOTTOM: 2,
        CAP_ALIGN_LEFT: 0,
        CAP_ALIGN_RIGHT: 1,
    }

    def __init__(self, params=None):
        if params is None:
            params = {}
        self._params = params

    @property
    def pos_weight(self):
       return (
             self.CAP_POS_WEIGHTS[self.valign] * 3 +
            self.CAP_POS_WEIGHTS[self.halign]
        )

    @property
    def name(self):
       return self._params.get('name')

    @name.setter
    def name(self, value):
       self._params['name'] = str(value)

    # @property
    # def pos_name(self):
    #   return self.valign + '_' + self.halign

    @property
    def vfrac(self):
        # Returns "visible length" of the text
        return self._params.get('vfrac', 1)

    @vfrac.setter
    def vfrac(self, value):
        self._params['vfrac'] = float(value)

    @property
    def text(self):
        return self._params.get('text', '')

    @property
    def text_length(self):
        return len(self.text)

    @text.setter
    def text(self, value):
        value  = re.sub("[\r\n]$", "", value)
        self._params['text'] = value

    @property
    def visible_text(self):
        text = self.text
        text = text[0: int(round(len(text) * self.vfrac))]
        if text is None:
            text = ''
        return text

    @property
    def focuser(self):
        return self._params.get('focuser', {
            'type': 'anchored_rect',
            'spread': 2
        })

    @property
    def focuser_fill_color(self):
        return self._params.get('focuser_fill_color')

    @focuser_fill_color.setter
    def focuser_fill_color(self, value):
        self._params['focuser_fill_color'] = value

    @property
    def valign(self):
        return self._params.get('valign', 'center')

    @property
    def halign(self):
        return self._params.get('halign', 'center')

    @halign.setter
    def halign(self, value):
        self._params['halign'] = value

    @property
    def padding(self):
        return int(self._params.get('padding', 2))

    @padding.setter
    def padding(self, value):
        self._params['padding'] = int(value)

    @property
    def margin(self):
        return int(self._params.get('margin', 2))

    @margin.setter
    def margin(self, value):
        self._params['margin'] = int(value)

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
        return self._params.get('back_color')

    @back_color.setter
    def back_color(self, value):
        self._params['back_color'] = value

    def get_json(self):
        data = dict(self._params)
        return data

    @classmethod
    def create_from_json(cls, data):
        newob = cls(data)
        return newob
