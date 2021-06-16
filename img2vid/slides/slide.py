import json
from operator import attrgetter

from ..effects import create_effect_from_json
from ..effects import NumberParamChange

class Slide:
    _IdSeed = 0
    TYPE_NAME = None
    KEY_TYPE = "type"
    KEY_EFFECTS = "effects"

    def __init__(self):
        self._id_num = Slide._IdSeed + 1
        self.effects = {}
        Slide._IdSeed = Slide._IdSeed + 1
        self.add_effect(NumberParamChange, {
            'param_name': 'vtext_frac',
            'value_start': 0,
            'value_end': 1,
            'scale': 3
        })

    @property
    def sorted_effects(self):
        return list(sorted(self.effects.values(), key=attrgetter('sort_weight')))

    @property
    def crop_allowed(self):
        return False

    def add_effect(self, effect_class, effect_data, name=None):
        effect_data['sort_weight'] = effect_data.get('sort_weight', len(self.effects))
        effect = effect_class.create_from_values(effect_data)
        if not name:
            name = effect.get_name()
        self.effects[name] = effect

    def remove_effect(self, effect_name):
        if effect_name in self.effects:
            del self.effects[effect_name]

    def get_json(self):
        data = {self.KEY_TYPE:self.TYPE_NAME}
        effects_data = []
        data[self.KEY_EFFECTS] = effects_data
        for flt in self.effects.values():
            effects_data.append(flt.get_json())
        return data

    def load_effects_from_json(self, data):
        if self.KEY_EFFECTS in data:
            for effect_data in data[self.KEY_EFFECTS]:
                flt = create_effect_from_json(effect_data)
                if flt:
                    self.effects[flt.get_name()] = flt

    @property
    def id_num(self):
        return self._id_num

    def __hash__(self):
        return hash("Slide{}".format(self._id_num))

    def __eq__(self, other):
        return isinstance(other, Slide) and other.id_num == self.id_num

    def clone(self):
        data = json.loads(json.dumps(self.get_json()))
        return self.create_from_json(data)
