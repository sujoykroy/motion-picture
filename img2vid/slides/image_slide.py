import re
import os
import tempfile
from operator import attrgetter

import requests

from ..effects import NumberParamChange
from .slide import Slide
from ..geom import Point, Rectangle
from .caption import Caption


class ImageSlide(Slide):
    URL_PATH_RE = re.compile(r'https?://')
    URL_CLEANER_RE = re.compile('[^a-zA-Z0-9_\?]')

    TYPE_NAME = "image"
    KEY_FILEPATH = "filepath"
    KEY_RECT = "rect"
    KEY_CAPTIONS = "caps"
    KEY_CAP_WIDTH_FRAC = "cap_width_frac"
    KEY_IMAGE_FIT = 'image_fit'
    KEY_ANGLE = 'angle'
    KEY_SCALE = 'scale'
    KEY_OFFSET_X = 'offset_x'
    KEY_OFFSET_Y = 'offset_y'

    CAP_ALIGN_TOP = Caption.CAP_ALIGN_TOP
    CAP_ALIGN_CENTER = Caption.CAP_ALIGN_CENTER
    CAP_ALIGN_BOTTOM = Caption.CAP_ALIGN_BOTTOM
    CAP_ALIGN_LEFT = Caption.CAP_ALIGN_LEFT
    CAP_ALIGN_RIGHT = Caption.CAP_ALIGN_RIGHT
    CAP_ALIGNMENTS = [CAP_ALIGN_TOP, CAP_ALIGN_CENTER, CAP_ALIGN_BOTTOM]

    ImageCache = {}
    TEMP_FOLDER = None

    CONSTRUCTOR_KEYS = Slide.CONSTRUCTOR_KEYS + [
        KEY_FILEPATH, KEY_RECT, KEY_CAPTIONS, KEY_CAP_WIDTH_FRAC,
        KEY_IMAGE_FIT, KEY_ANGLE, KEY_SCALE,
        KEY_OFFSET_X, KEY_OFFSET_Y]

    THROTTLE_KEYS = Slide.THROTTLE_KEYS + [KEY_IMAGE_FIT]

    def __init__(self, filepath, rect=None, **kwargs):
        super().__init__(**kwargs)
        filepath = filepath or ''
        self._filepath = filepath
        self._local_filepath = filepath
        if self.URL_PATH_RE.match(filepath):
            self._local_filepath = ImageSlide.ImageCache.get(filepath)
            if not ImageSlide.TEMP_FOLDER:
                ImageSlide.TEMP_FOLDER = tempfile.TemporaryDirectory()
            if not self._local_filepath:
                self._local_filepath = os.path.join(
                    ImageSlide.TEMP_FOLDER.name,
                    self.URL_CLEANER_RE.sub("", filepath).split("?")[0]
                )
                req = requests.get(filepath)
                with open(self._local_filepath, "wb") as fp:
                    fp.write(req.content)
                ImageSlide.ImageCache[filepath] = self._local_filepath
        self._rect = rect
        self._captions = kwargs.get(self.KEY_CAPTIONS)
        self.angle = float(kwargs.get(self.KEY_ANGLE) or 0)
        self.scale = float(kwargs.get(self.KEY_SCALE) or 1)
        self.offset_x = float(kwargs.get(self.KEY_OFFSET_X) or 0)
        self.offset_y = float(kwargs.get(self.KEY_OFFSET_Y) or 0)

        if self._captions is None:
            self._captions = []
        if isinstance(self._captions, dict):
            self._captions = self._captions.values()

        # for valign in self.CAP_ALIGNMENTS:
        #    self._captions.append(Caption(
        #        {'valign': valign, 'halign': 'center', 'text': ''}
        #    )
        self.cap_width_frac = kwargs.get(self.KEY_CAP_WIDTH_FRAC) or 0.9

        self.image_fit = kwargs.get(self.KEY_IMAGE_FIT)

    @property
    def fit_image_full(self):
        if not self.image_fit:
            return True
        return self.image_fit == 'full'

    def get_caption(self, valign):
        for cap in self._captions:
            if cap.valign == valign:
                return cap
        cap = Caption(params={'valign': valign, 'text': ''})
        self.set_caption(cap)
        return cap

    def set_caption(self, caption):
        self._captions.append(caption)

    @property
    def text_length(self):
        length = 0;
        for cap in self._captions:
            length += cap.text_length
        return length

    @property
    def vtext_frac(self):
        return 1

    @vtext_frac.setter
    def vtext_frac(self, value):
        total_text_length = self.text_length
        running_length = 0
        vtext_length = total_text_length * value
        for cap in self.active_captions:
            if running_length > vtext_length or not cap.text_length:
                cap.vfrac = 0
            else:
                cap.vfrac = (vtext_length - running_length)/ cap.text_length
            running_length += cap.text_length

    @property
    def caps(self):
        return self._captions

    @property
    def named_caps(self):
        caps_dict = {}
        for cap in self._captions:
            if cap.name:
                caps_dict[cap.name] = cap
        return caps_dict

    @property
    def caps(self):
        return self._captions

    @property
    def active_captions(self):
        caps = []
        for cap in self._captions:
            if cap.text:
                caps.append(cap)

        caps = list(sorted(caps, key=attrgetter('pos_weight')))
        return caps

    @property
    def has_caption(self):
        for cap in self._captions:
            if cap.text:
                return True
        return False

    @property
    def crop_allowed(self):
        return True

    @property
    def filepath(self):
        return self._filepath

    @property
    def local_filepath(self):
        return self._local_filepath

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect):
        if not self._rect:
            self._rect = Rectangle(0, 0, 1, 1)
        self._rect.copy_from(rect)

    def crop(self, rect):
        if self._rect:
            rect = rect.copy()
            rect.translate(Point(self._rect.x1, self._rect.y1))
        newob = ImageSlide(self._filepath, rect)
        return newob

    def get_json(self):
        data = super().get_json()
        if self._rect:
            data[self.KEY_RECT] = self._rect.get_json()
        data[self.KEY_CAPTIONS] = []
        for caption in self._captions:
            if caption.text:
                data[self.KEY_CAPTIONS].append(caption.get_json())
        return data

    @classmethod
    def create_from_json(cls, data):
        rect = data.pop(cls.KEY_RECT, None)
        captions = data.pop(cls.KEY_CAPTIONS, {})
        if rect:
            rect = Rectangle.create_from_json(rect)
        caps = []
        for caption_data in captions:
            caps.append(Caption.create_from_json(caption_data))
        newob = super().create_from_json({'rect': rect, 'caps': caps, **data})
        return newob
