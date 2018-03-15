from ..geom import Point, Rectangle
from ..utils import VideoCache

from .image_slide import ImageSlide
from .caption import Caption

class VideoSlide(ImageSlide):
    TYPE_NAME = "video"
    KEY_START_AT = "start_at"
    KEY_END_AT = "end_at"
    KEY_ABS_CURR_POS = "abs_pos"

    def __init__(self, filepath, rect=None):
        super().__init__(filepath, rect)
        self._start_at = 0
        self._end_at = -1
        self._abs_current_pos = 0
        self._duration = None
        self._full_duration = None

    @property
    def abs_current_pos(self):
        return self._abs_current_pos

    @abs_current_pos.setter
    def abs_current_pos(self, value):
        self._abs_current_pos = value

    @property
    def current_pos(self):
        return self._abs_current_pos-self._start_at

    @current_pos.setter
    def current_pos(self, value):
        self._abs_current_pos = self._start_at + value

    @property
    def full_duration(self):
        if self._full_duration is None:
            self._full_duration = VideoCache.get_video_clip(self.filepath).reader.duration
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

    @property
    def duration(self):
        return self.end_at-self.start_at

    def crop(self, rect):
        if self._rect:
            rect = rect.copy()
            rect.translate(Point(self._rect.x1, self._rect.y1))
        newob = VideoSlide(self._filepath, rect)
        newob.start_at = self.start_at
        newob.end_at = self.end_at
        newob.abs_current_pos = self.abs_current_pos
        return newob

    def get_json(self):
        data = super().get_json()
        data[self.KEY_START_AT] = self._start_at
        data[self.KEY_END_AT] = self._end_at
        data[self.KEY_ABS_CURR_POS] = self._abs_current_pos
        return data

    @classmethod
    def create_from_json(cls, data):
        newob = super().create_from_json(data)
        newob.start_at = data.get(cls.KEY_START_AT, 0)
        newob.end_at = data.get(cls.KEY_END_AT, -1)
        newob.abs_current_pos = data.get(cls.KEY_ABS_CURR_POS, 0)
        return newob
