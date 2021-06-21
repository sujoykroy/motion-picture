import re

from ..geom import Point, Rectangle
from ..utils import VideoCache

from .image_slide import ImageSlide
from .caption import Caption

class VideoSlide(ImageSlide):
    TYPE_NAME = "video"
    KEY_START_AT = "start_at"
    KEY_END_AT = "end_at"
    KEY_ABS_CURR_POS = "abs_pos"
    KEY_LOOP_MODE = "loop_mode"

    LOOP_START = "start"
    LOOP_REVERSE = "reverse"

    CONSTRUCTOR_KEYS = ImageSlide.CONSTRUCTOR_KEYS + [
        KEY_START_AT, KEY_END_AT, KEY_ABS_CURR_POS,
        KEY_LOOP_MODE
    ]

    VIDEO_FILEPATH_PAT = re.compile(r'\.(mov|mp4|mpg|mpeg)$')


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._start_at = kwargs.get(self.KEY_START_AT) or 0
        self._end_at =  kwargs.get(self.KEY_END_AT) or -1
        self._abs_current_pos =  kwargs.get(self.KEY_ABS_CURR_POS) or 0
        self._full_duration = None
        self.loop_mode = kwargs.get(self.KEY_LOOP_MODE) or self.LOOP_START
    
    @property
    def abs_pos(self):
        return self._abs_current_pos

    @property
    def abs_current_pos(self):
        return self._abs_current_pos

    @abs_current_pos.setter
    def abs_current_pos(self, value):
        self._abs_current_pos = value

    @property
    def current_pos(self):
        return self._abs_current_pos-self._start_at


    @property
    def span(self):
        return self._end_at - self._start_at

    @current_pos.setter
    def current_pos(self, value):
        span = self.span
        if value > span:
            if self.loop_mode == self.LOOP_START:
                value %= span
                print(value)
            elif self.loop_mode == self.LOOP_REVERSE:
                value %= span * 2
                if value > span:
                    value = span - (value - span)

        self._abs_current_pos = self._start_at + value


    @property
    def full_duration(self):
        if self._full_duration is None:
            self._full_duration = VideoCache.get_video_clip(self.filepath).duration
            VideoCache.clear_cache()#Hack to prevent uknown preview lock
        return self._full_duration

    @property
    def end_at(self):
        if self._end_at<0:
            self._end_at = self.full_duration
        return self._end_at

    @end_at.setter
    def end_at(self, value):
        self._end_at = min(self.full_duration, value)

    @property
    def start_at(self):
        return self._start_at

    @start_at.setter
    def start_at(self, value):
        self._start_at = max(0, value)

    def crop(self, rect):
        if self._rect:
            rect = rect.copy()
            rect.translate(Point(self._rect.x1, self._rect.y1))
        newob = VideoSlide(self._filepath, rect)
        newob.start_at = self.start_at
        newob.end_at = self.end_at
        newob.abs_current_pos = self.abs_current_pos
        return newob

    @classmethod
    def check_if_file_supported(cls, filepath):
        return bool(cls.VIDEO_FILEPATH_PAT.search(filepath))
