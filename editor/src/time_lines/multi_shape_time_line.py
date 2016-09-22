from ..commons import *
from xml.etree.ElementTree import Element as XmlElement
from shape_time_line import ShapeTimeLine

class MultiShapeTimeLine(object):
    TAG_NAME = "multi_shape_time_line"

    def __init__(self, name=None, duration=0.):
        self.shape_time_lines = OrderedDict()
        self.duration = duration
        self.name = name

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["name"] = self.name
        for shape_time_line in self.shape_time_lines:
            elm.append(shape_time_line.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm, multi_shape):
        multi_shape_time_line = cls(name=elm.attrib["name"])
        for shape_time_line_elm in elm.findall(ShapeTimeLine.TAG_NAME):
            shape_time_line = ShapeTimeLine.create_from_xml_element(shape_time_line_elm, multi_shape)
            multi_shape_time_line.shape_time_lines.add(shape_time_line.shape, shape_time_line)
        multi_shape_time_line.get_duration()
        return multi_shape_time_line

    def get_prop_count(self):
        prop_count = 0
        for shape_time_line in self.shape_time_lines:
            prop_count += shape_time_line.get_prop_count()
        return prop_count

    def add_shape_prop_time_slice(self, shape, prop_name, time_slice):
        if not self.shape_time_lines.key_exists(shape):
            shape_time_line = ShapeTimeLine(shape)
            self.shape_time_lines.add(shape, shape_time_line)
        else:
            shape_time_line = self.shape_time_lines[shape]
        shape_time_line.add_prop_time_slice(prop_name, time_slice)
        self.get_duration()

    def remove_shape_prop_time_slice(self, shape, prop_name, time_slice):
        if not self.shape_time_lines.key_exists(shape): return
        shape_time_line = self.shape_time_lines[shape]
        shape_time_line.remove_prop_time_slice(prop_name, time_slice)
        if len(shape_time_line.prop_time_lines)==0:
            self.shape_time_lines.remove(shape)
        self.get_duration()

    def insert_shape_prop_time_slice_at(self, t, shape, prop_name, time_slice):
        if not self.shape_time_lines.key_exists(shape):
            shape_time_line = ShapeTimeLine(shape)
            self.shape_time_lines.add(shape, shape_time_line)
        else:
            shape_time_line = self.shape_time_lines[shape]
        shape_time_line.insert_prop_time_slice_at(t, prop_name, time_slice)
        self.get_duration()

    def move_to(self, t):
        for shape_time_line in self.shape_time_lines:
            shape_time_line.move_to(t)

    def get_duration(self):
        duration = 0
        for shape_time_line in self.shape_time_lines:
            shape_duration = shape_time_line.get_duration()
            if duration < shape_duration:
                duration = shape_duration
        self.duration = duration
        return duration

    def expand_shape_time_lines_duration(self):
        for shape_time_line in self.shape_time_lines:
            shape_time_line.expand_duration(self.duration)

