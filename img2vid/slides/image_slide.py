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

    CAP_ALIGN_TOP = Caption.CAP_ALIGN_TOP
    CAP_ALIGN_CENTER = Caption.CAP_ALIGN_CENTER
    CAP_ALIGN_BOTTOM = Caption.CAP_ALIGN_BOTTOM
    CAP_ALIGN_LEFT = Caption.CAP_ALIGN_LEFT
    CAP_ALIGN_RIGHT = Caption.CAP_ALIGN_RIGHT
    CAP_ALIGNMENTS = [CAP_ALIGN_TOP, CAP_ALIGN_CENTER, CAP_ALIGN_BOTTOM]

    ImageCache = {}
    TEMP_FOLDER = None

    CONSTRUCTOR_KEYS = Slide.CONSTRUCTOR_KEYS + [
        KEY_FILEPATH, KEY_RECT, KEY_CAPTIONS]

    def __init__(self, filepath, rect=None, **kwargs):
        super().__init__(**kwargs)
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
        if self._captions is None:
            self._captions = {}

        for valign in self.CAP_ALIGNMENTS:
            self._captions[valign] = Caption(
                {'valign': valign, 'text': ''})


        self.add_effect(NumberParamChange, {
            'param_name': 'vtext_frac',
            'value_start': 0,
            'value_end': 1,
            'scale': 3
        })

    def get_caption(self, valign):
        return self._captions[valign]

    def set_caption(self, caption):
        self._captions[caption.pos_name] = caption

    @property
    def text_length(self):
        length = 0;
        for cap in self._captions.values():
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
    def active_captions(self):
        caps = []
        for cap in self._captions.values():
            if cap.text:
                caps.append(cap)

        caps = list(sorted(caps, key=attrgetter('pos_weight')))
        return caps

    @property
    def has_caption(self):
        for cap in self._captions.values():
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
        for caption in self._captions.values():
            if caption.text:
                data[self.KEY_CAPTIONS].append(caption.get_json())
        return data

    @classmethod
    def create_from_json(cls, data):
        rect = data.pop(cls.KEY_RECT, None)
        captions = data.pop(cls.KEY_CAPTIONS, {})
        if rect:
            rect = Rectangle.create_from_json(rect)
        newob = super().create_from_json({'rect': rect, **data})
        for caption_data in captions:
            caption = Caption.create_from_json(caption_data)
            newob.set_caption(caption)
        return newob
