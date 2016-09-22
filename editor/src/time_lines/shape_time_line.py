from xml.etree.ElementTree import Element as XmlElement
from ..commons import *
from prop_time_line import PropTimeLine

class ShapeTimeLine(object):
    TAG_NAME = "shape_time_line"
    SHAPE_NAME = "shape_name"

    def __init__(self, shape):
        self.shape = shape
        self.prop_time_lines = OrderedDict()

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib[self.SHAPE_NAME] = self.shape.get_name()
        for prop_time_line in self.prop_time_lines:
            elm.append(prop_time_line.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm, multi_shape):
        shape=multi_shape.shapes[elm.attrib[cls.SHAPE_NAME]]
        shape_time_line = cls(shape)
        for prop_time_line_elm in elm.findall(PropTimeLine.TAG_NAME):
            prop_time_line = PropTimeLine.create_from_xml_element(prop_time_line_elm, shape)
            shape_time_line.prop_time_lines.add(prop_time_line.prop_name, prop_time_line)
        return shape_time_line

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

    def move_to(self, t):
        for prop_time_line in self.prop_time_lines:
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

