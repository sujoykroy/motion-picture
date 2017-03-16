from ..commons import *
from xml.etree.ElementTree import Element as XmlElement
from shape_time_line import ShapeTimeLine

class MultiShapeTimeLine(object):
    TAG_NAME = "multi_shape_time_line"

    def __init__(self, name=None, duration=0.):
        self.shape_time_lines = OrderedDict()
        self.duration = duration
        self.name = name
        self.time_labels = []
        self.time_markers = dict()

    def add_time_marker(self, at, error_span):
        if at in self.time_markers:
            return None
        for exist_at in sorted(self.time_markers.keys()):
            if abs(exist_at-at)<=error_span:
                return None
        time_marker = TimeMarker(at, "{0:.02f}".format(at))
        self.time_markers[time_marker.at] = time_marker
        return time_marker

    def delete_time_marker(self, at):
        if at in self.time_markers:
            del self.time_markers[at]

    def move_time_marker(self, at, to):
        if to in self.time_markers:
            return False
        self.time_markers[to] = self.time_markers[at]
        self.time_markers[at].at = to
        del self.time_markers[at]
        return True

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
            if not shape_time_line: continue
            multi_shape_time_line.shape_time_lines.add(shape_time_line.shape, shape_time_line)
        multi_shape_time_line.get_duration()
        return multi_shape_time_line

    def copy(self, shapes):
        newob = MultiShapeTimeLine(name=self.name)
        for orig_shape in self.shape_time_lines.keys:
            new_shape = shapes[orig_shape.get_name()]
            newob.shape_time_lines.add(
                new_shape,
                self.shape_time_lines[orig_shape].copy(new_shape))
        newob.duration = self.duration
        return newob

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

    def remove_shape(self, shape):
        self.shape_time_lines.remove(shape)

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

