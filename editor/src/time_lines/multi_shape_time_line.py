from ..commons import *
from xml.etree.ElementTree import Element as XmlElement
from shape_time_line import ShapeTimeLine
from time_marker import TimeMarker
from ..shapes.audio_shape import AudioShape
from audio_clip_generator import AudioClipGenerator

class MultiShapeTimeLine(object):
    TAG_NAME = "multi_shape_time_line"

    def __init__(self, multi_shape, name=None, duration=0., ):
        self.shape_time_lines = OrderedDict()
        self.multi_shape = multi_shape
        self.duration = duration
        self.name = name
        self.time_labels = []
        self.time_markers = dict()

    def set_name(self, name):
        self.name = name

    def add_time_marker(self, at, error_span):
        if at in self.time_markers:
            return None
        if self.get_closest_time_marker(at, error_span) is not None:
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
        tmk = self.time_markers.get(at)
        if tmk is None:
            return False
        self.time_markers[to] = tmk
        self.time_markers[at].at = to
        del self.time_markers[at]
        return True

    def get_closest_time_marker(self, at, error_span):
        for exist_at in sorted(self.time_markers.keys()):
            if abs(exist_at-at)<=error_span:
                return self.time_markers[exist_at]
        return None

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["name"] = self.name
        for shape_time_line in self.shape_time_lines:
            shape_time_elm = shape_time_line.get_xml_element()
            if shape_time_line.shape == self.multi_shape:
                del shape_time_elm.attrib[ShapeTimeLine.SHAPE_NAME]
            elm.append(shape_time_elm)
        for time_marker in self.time_markers.values():
            elm.append(time_marker.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm, multi_shape):
        multi_shape_time_line = cls(name=elm.attrib["name"], multi_shape=multi_shape)
        for shape_time_line_elm in elm.findall(ShapeTimeLine.TAG_NAME):
            shape_time_line = ShapeTimeLine.create_from_xml_element(shape_time_line_elm, multi_shape)
            if not shape_time_line: continue
            if shape_time_line.shape == multi_shape:
                shape_time_line.set_display_name("self")
            multi_shape_time_line.shape_time_lines.add(shape_time_line.shape, shape_time_line)
        for time_marker_elm in elm.findall(TimeMarker.TAG_NAME):
            time_marker = TimeMarker.create_from_xml_element(time_marker_elm)
            if time_marker is None:
                continue
            multi_shape_time_line.time_markers[time_marker.at] = time_marker
        multi_shape_time_line.get_duration()
        return multi_shape_time_line

    def copy(self, multi_shape=None):
        if multi_shape is None:
            multi_shape = self.multi_shape
        newob = MultiShapeTimeLine(name=self.name, multi_shape=multi_shape)
        for orig_shape in self.shape_time_lines.keys:
            if orig_shape == self.multi_shape:
                new_shape = multi_shape
            else:
                new_shape = self.multi_shape.shapes[orig_shape.get_name()]
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
        if not self.is_safe_to_add(shape, prop_name, time_slice):
            return
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
        if not self.is_safe_to_add(shape, prop_name, time_slice):
            return
        if not self.shape_time_lines.key_exists(shape):
            shape_time_line = ShapeTimeLine(shape)
            self.shape_time_lines.add(shape, shape_time_line)
        else:
            shape_time_line = self.shape_time_lines[shape]
        if shape_time_line.shape == self.multi_shape:
            shape_time_line.set_display_name("self")
        shape_time_line.insert_prop_time_slice_at(t, prop_name, time_slice)
        self.get_duration()

    def is_safe_to_add(self, shape, prop_name, time_slice):
        if prop_name.find("tm_") ==0 and shape == self.multi_shape:
            if prop_name[3:] == self.name:
                return False
        return True

    def remove_shape(self, shape):
        self.shape_time_lines.remove(shape)

    def move_to(self, t, force_visible=True):
        for shape, shape_time_line in self.shape_time_lines.iter_key_values():
            if force_visible:
                shape.visible = True
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

    def get_audio_clips(self):
        audio_clips = []
        for shape_line in self.shape_time_lines:
            shape = shape_line.shape
            if not isinstance(shape, AudioShape):
                continue
            for prop_line in shape_line.prop_time_lines:
                if prop_line.prop_name != "time_pos":
                    continue
                t = 0
                for time_slice in prop_line.time_slices:
                    clip = AudioClipGenerator(shape, time_slice)
                    clip = clip.set_start(t)
                    audio_clips.append(clip)
                    t += time_slice.duration
        return audio_clips
