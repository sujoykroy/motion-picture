from xml.etree.ElementTree import Element as XmlElement
from ..commons import *
from time_slice import TimeSlice

class PropTimeLine(object):
    TAG_NAME = "prop_time_line"
    PROP_NAME = "prop_name"

    def __init__(self, shape, prop_name):
        self.shape = shape
        self.prop_name = prop_name
        self.time_slices = OrderedDict()

    def is_time_slice_linkable(self):
        return not self.prop_name in('internal', "time_pos")

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib[self.PROP_NAME] = self.prop_name
        for time_slice in self.time_slices :
            elm.append(time_slice.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm, shape):
        prop_name = elm.attrib[cls.PROP_NAME]
        prop_time_line = cls(shape, prop_name)
        for time_slice_elm in elm.findall(TimeSlice.TAG_NAME):
            time_slice = TimeSlice.create_from_xml_element(time_slice_elm)
            if time_slice:
                #temporary, transition
                if prop_name == "time_pos" and "av_filename" in time_slice.prop_data:
                    class_name = shape.__class__.__name__
                    if class_name == "AudioShape":
                        path = "audio"
                    elif class_name == "VideoShape":
                        path = "video"
                    time_slice.prop_data[path + "_path"] = time_slice.prop_data["av_filename"]
                    del time_slice.prop_data["av_filename"]
                prop_time_line.time_slices.add(time_slice, time_slice)
        return prop_time_line

    def copy(self, shape):
        newob = PropTimeLine(shape, self.prop_name)
        for key in self.time_slices.keys:
            time_slice = self.time_slices[key].copy()
            newob.time_slices.add(time_slice, time_slice)
        return newob

    def add_time_slice(self, time_slice):
        self.time_slices.add(time_slice, time_slice)

    def remove_time_slice(self, time_slice):
        self.time_slices.remove(time_slice)

    def insert_time_slice_at(self, t, time_slice):
        if len(self.time_slices) == 0:
            time_slice.duration += t
            self.add_time_slice(time_slice)
            return
        if t == 0: return
        elapsed = 0
        inserted = False
        prev_time_slice = None
        for i in range(len(self.time_slices.keys)):
            exist_time_slice = self.time_slices[self.time_slices.keys[i]]
            if t<elapsed+exist_time_slice.duration:
                remaining_time = elapsed+exist_time_slice.duration - t
                if remaining_time>1/25.:
                    exist_time_slice.duration = t - elapsed
                    time_slice.duration = remaining_time
                    if self.is_time_slice_linkable():
                        exist_time_slice.end_value = time_slice.start_value
                        exist_time_slice.linked_to_next = True
                        time_slice.linked_to_next = True
                    self.time_slices.insert_after(exist_time_slice, time_slice, time_slice)
                inserted = True
                break
            elapsed += exist_time_slice.duration
            prev_time_slice = exist_time_slice

        if not inserted:
            last_time_slice = self.time_slices.get_last_item()
            last_value = last_time_slice.value_at(last_time_slice.duration)
            prop_data = None
            if last_time_slice.prop_data:
                prop_data = last_time_slice.prop_data.copy()
            inter_time_slice = TimeSlice(last_value, time_slice.start_value,
                                t-elapsed, prop_data=prop_data)
            if self.is_time_slice_linkable():
                last_time_slice.linked_to_next = True
                inter_time_slice.linked_to_next = True
                time_slice.linked_to_next = True
            self.time_slices.insert_after(last_time_slice, inter_time_slice, inter_time_slice)
            self.time_slices.insert_after(inter_time_slice, time_slice, time_slice)

        self.add_time_slice(time_slice)

    def move_to(self, t):
        elapsed = 0
        slice_count = len(self.time_slices.keys)
        for i in range(slice_count):
            time_slice = self.time_slices[self.time_slices.keys[i]]
            if t<elapsed+time_slice.duration or i==slice_count-1:
                if t>elapsed+time_slice.duration:
                    t = elapsed+time_slice.duration
                value = time_slice.value_at(t - elapsed)
                self.shape.set_prop_value(self.prop_name, value, time_slice.prop_data)
                return
            elapsed += time_slice.duration
        return None

    def __iter__(self):
        for time_slice in self.time_slices:
            yield time_slice

    def get_duration(self):
        duration = 0
        for time_slice in self.time_slices:
            duration += time_slice.duration
        return duration

    def expand_duration(self, duration):
        self_duration = self.get_duration()
        if self_duration<duration:
            self.time_slices[-1].duration += duration - self_duration

    def get_min_max_value(self):
        pmax = pmin = None
        for time_slice in self.time_slices:
            tmin, tmax = time_slice.get_min_max_value()
            if pmax is None or pmax<tmax: pmax = tmax
            if pmin is None or pmin>tmin: pmin = tmin
        return pmin, pmax

    def sync_time_slices_with_time_markers(self, time_markers):
        slice_count = len(self.time_slices.keys)
        time_marker_texts = [tm.get_text() for tm in time_markers]
        elapsed = 0
        for i in range(slice_count):
            time_slice = self.time_slices[self.time_slices.keys[i]]
            if time_slice.end_marker in time_marker_texts:
                index = time_marker_texts.index(time_slice.end_marker)
                time_marker = time_markers[index]
                duration = time_marker.at-elapsed
                if duration>0:
                    time_slice.duration = duration
            elapsed += time_slice.duration

    def rename_time_slice_end_markers(self, old_marker, new_marker):
        for time_slice in self.time_slices:
            if time_slice.end_marker == old_marker:
                time_slice.end_marker = new_marker
