from xml.etree.ElementTree import Element as XmlElement
from ..commons import *
from .prop_time_line import PropTimeLine
from ..shapes import CurvePointGroupShape

class ShapeTimeLine(object):
    TAG_NAME = "shape_time_line"
    SHAPE_NAME = "shape_name"

    def __init__(self, shape):
        self.shape = shape
        self.prop_time_lines = OrderedDict()
        self._display_name = None

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib[self.SHAPE_NAME] = self.shape.get_name()
        for prop_time_line in self.prop_time_lines:
            elm.append(prop_time_line.get_xml_element())
        return elm

    def get_display_name(self):
        if self._display_name:
            return self._display_name
        return self.shape.get_name()

    def set_display_name(self, display_name):
        self._display_name = display_name

    @classmethod
    def create_from_xml_element(cls, elm, multi_shape):
        shape_name = elm.attrib.get(cls.SHAPE_NAME, None)
        if shape_name is None:
            shape = multi_shape
        else:
            if not multi_shape.shapes.contain(shape_name): return None
            shape=multi_shape.shapes[shape_name]
        shape_time_line = cls(shape)

        for prop_time_line_elm in elm.findall(PropTimeLine.TAG_NAME):
            prop_time_line = PropTimeLine.create_from_xml_element(prop_time_line_elm, shape)
            shape_time_line.prop_time_lines.add(prop_time_line.prop_name, prop_time_line)
        return shape_time_line

    def copy(self, shape):
        newob = ShapeTimeLine(shape)
        for key in self.prop_time_lines.keys:
            newob.prop_time_lines.add(key, self.prop_time_lines[key].copy(shape))
        return newob

    def add_prop_time_slice(self, prop_name, time_slice):
        if not self.prop_time_lines.key_exists(prop_name):
            prop_time_line = PropTimeLine(self.shape, prop_name)
            self.prop_time_lines.add(prop_name, prop_time_line)
        else:
            prop_time_line = self.prop_time_lines[prop_name]
        prop_time_line.add_time_slice(time_slice)

    def remove_prop_time_slice(self, prop_name, time_slice):
        if not self.prop_time_lines.key_exists(prop_name): return
        prop_time_line = self.prop_time_lines[prop_name]
        prop_time_line.remove_time_slice(time_slice)
        if len(prop_time_line.time_slices) == 0:
            self.prop_time_lines.remove(prop_name)

    def insert_prop_time_slice_at(self, t, prop_name, time_slice):
        if not self.prop_time_lines.key_exists(prop_name):
            prop_time_line = PropTimeLine(self.shape, prop_name)
            self.prop_time_lines.add(prop_name, prop_time_line)
        else:
            prop_time_line = self.prop_time_lines[prop_name]
        prop_time_line.insert_time_slice_at(t, time_slice)

    def move_to(self, t, audio_only=False):
        for prop_time_line in self.prop_time_lines:
            if audio_only:
                if self.shape.__class__.__name__ not in ("AudioShape", "VideoShape"):
                    continue
                if prop_time_line.prop_name != "time_pos":
                    continue
            prop_time_line.move_to(t)

    def expand_duration(self, duration):
        for prop_time_line in self.prop_time_lines:
            prop_time_line.expand_duration(duration)

    def get_prop_count(self):
        return len(self.prop_time_lines)

    def get_duration(self):
        duration = 0
        for prop_time_line in self.prop_time_lines:
            prop_duration = prop_time_line.get_duration()
            if duration < prop_duration:
                duration = prop_duration
        return duration

    def sync_time_slices_with_time_markers(self, time_markers):
        for prop_time_line in self.prop_time_lines:
            prop_time_line.sync_time_slices_with_time_markers(time_markers)

    def rename_time_slice_end_markers(self, old_marker, new_marker):
        for prop_time_line in self.prop_time_lines:
            prop_time_line.rename_time_slice_end_markers(old_marker, new_marker)
