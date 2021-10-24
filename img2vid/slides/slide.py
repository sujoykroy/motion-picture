import json
from operator import attrgetter

from ..effects import create_effect_from_json
from ..utils.value_parser import ValueParser


class Slide:
    _IdSeed = 0
    TYPE_NAME = None
    KEY_TYPE = "type"
    KEY_EFFECTS = "effects"
    KEY_MASK_SLIDE = 'mask_slide'
    KEY_OPACITY = 'opacity'
    KEY_SUB_SLIDES = 'sub_slides'
    KEY_DURATION = 'duration'
    KEY_DELAY = 'delay'
    KEY_AREA = 'area'
    KEY_VALIGN = 'area'
    KEY_HALIGN = 'area'

    CONSTRUCTOR_KEYS = [KEY_OPACITY, KEY_DURATION, KEY_DELAY, KEY_AREA,
        KEY_VALIGN, KEY_HALIGN]
    THROTTLE_KEYS = [KEY_OPACITY, KEY_DURATION, KEY_DELAY, KEY_AREA,
        KEY_VALIGN, KEY_HALIGN]

    def __init__(self, opacity=1, duration=None, delay=None, **kwargs):
        self._id_num = Slide._IdSeed + 1
        self.effects = {}
        Slide._IdSeed = Slide._IdSeed + 1
        self.mask_slide = None
        if opacity is None:
            opacity = 1
        self.opacity = opacity
        self.sub_slides = []
        if duration is not None:
            duration = float(duration)
        self.duration = duration
        if delay is not None:
            delay = float(delay)
        self.delay = delay
        self._area = kwargs.get('area')
        self.valign = kwargs.get('valign')
        self.halign = kwargs.get('halign')

    @property
    def area(self):
        return self._area or {}

    @area.setter
    def area(self, value):
        if value:
            value = dict(value)
        else:
            value = None
        self._area = value

    @property
    def area_left_frac(self):
        return ValueParser.parse_float(self.area.get('left', 0), 0)/100

    @property
    def area_right_frac(self):
        return ValueParser.parse_float(self.area.get('right', 0), 0) / 100

    @property
    def area_top_frac(self):
        return ValueParser.parse_float(self.area.get('top', 0), 0) / 100

    @property
    def area_bottom_frac(self):
        return ValueParser.parse_float(self.area.get('bottom', 0), 0) / 100

    @property
    def area_width_frac(self):
        return 1 - self.area_right_frac - self.area_left_frac

    @property
    def area_height_frac(self):
        return 1 - self.area_bottom_frac - self.area_top_frac

    def set_mask_slide(self, mask_slide):
        self.mask_slide = mask_slide

    def add_sub_slide(self, sub_slide):
        self.sub_slides.append(sub_slide)

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
        data = {self.KEY_TYPE: self.TYPE_NAME}
        for key in self.CONSTRUCTOR_KEYS:
            data[key] = getattr(self, key)
        effects_data = {}
        data[self.KEY_EFFECTS] = effects_data
        for flt_name, flt in self.effects.items():
            effects_data[flt_name] = flt.get_json()
        if self.mask_slide:
            data[self.KEY_MASK_SLIDE] = self.mask_slide.get_json()
        if self.sub_slides:
            data[self.KEY_SUB_SLIDES] = []
            for sub_slide in self.sub_slides:
                data[self.KEY_SUB_SLIDES].append(sub_slide.get_json())

        for key in self.THROTTLE_KEYS:
            if data[key] is None:
                del data[key]
        return data

    def load_effects_from_json(self, data):
        if self.KEY_EFFECTS in data:
            effects_data = data[self.KEY_EFFECTS]

            if isinstance(effects_data, list): # Backward compatibility
                effects_data = dict(list(map(
                    lambda flt: (create_effect_from_json(flt).get_name(), flt),
                    effects_data
                )))

            for eff_name, effect_data in effects_data.items():
                flt = create_effect_from_json(effect_data)
                if flt:
                    self.effects[eff_name] = flt

    @property
    def id_num(self):
        return self._id_num

    def __hash__(self):
        return hash("Slide{}".format(self._id_num))

    def __eq__(self, other):
        return isinstance(other, Slide) and other.id_num == self.id_num

    @classmethod
    def create_from_json(cls, data):
        constr_data = {}
        for key in cls.CONSTRUCTOR_KEYS:
            constr_data[key] = data.get(key)
        newob = cls(**constr_data)
        newob.load_effects_from_json(data)
        return newob

    def clone(self):
        data = json.loads(json.dumps(self.get_json()))
        return self.create_from_json(data)
