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

    def get_time_markers_after(self, time_marker, non_fixed_only=False):
        keys = sorted(self.time_markers.keys())
        if time_marker.at in keys:
            index = keys.index(time_marker.at)
            keys = keys[index+1:]
            markers = []
            for key in keys:
                tmk = self.time_markers[key]
                if non_fixed_only and tmk.fixed:
                    continue
                markers.append(tmk)
            return markers
        else:
            return []

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

    def move_time_marker(self, at, to, move_others):
        if to in self.time_markers:
            return False
        tmk = self.time_markers.get(at)
        if tmk is None:
            return False

        if not tmk.fixed:
            keys = sorted(self.time_markers.keys())
            index = keys.index(at)
            for i in range(index-1, -1, -1):
                prev_tmk = self.time_markers.get(keys[i])
                if not prev_tmk.fixed:
                    if to<= prev_tmk.at:
                        return False
                    break

        if not tmk.fixed and move_others:
            after_markers = self.get_time_markers_after(tmk, non_fixed_only=True)
            keys = []
            changed_markers = []
            for after_marker in after_markers:
                if after_marker.fixed:#over conservative checking :-)
                    continue
                distance = after_marker.at-at
                if distance<=0:#over conservative checking :-)
                    continue
                del self.time_markers[after_marker.at]
                after_marker.at = to+distance
                changed_markers.append(after_marker)

            for after_marker in changed_markers:
                self.time_markers[after_marker.at] = after_marker

        del self.time_markers[at]
        tmk.at = to
        self.time_markers[to] = tmk
        self.sync_time_slices_with_time_marker(tmk)
        return True

    def get_closest_time_marker(self, at, error_span):
        for exist_at in sorted(self.time_markers.keys()):
            if abs(exist_at-at)<=error_span:
                return self.time_markers[exist_at]
        return None

    def get_time_marker_by_text(self, time_marker_text):
        for time_marker in self.time_markers.values():
            if time_marker.text == time_marker_text:
                return time_marker
        return None

    def get_time_marker_names(self):
        names = []
        for time_marker in self.time_markers.values():
            names.append(time_marker.text)
        return names

    def update_time_marker(self, orig_time_marker, other_time_marker):
        exist_time_marker = self.get_time_marker_by_text(other_time_marker.text)
        if exist_time_marker is None:
            old_text = orig_time_marker.text
            orig_time_marker.set_text(other_time_marker.text)
            for shape_time_line in self.shape_time_lines:
                shape_time_line.rename_time_slice_end_markers(old_text, other_time_marker.text)
        orig_time_marker.set_at(other_time_marker.at)
        orig_time_marker.set_fixed(other_time_marker.fixed)

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
                new_shape = multi_shape.shapes[orig_shape.get_name()]
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
            if force_visible and shape.renderable:
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

    def get_audio_clips(self, abs_time_offset=0, pre_scale=1.,
                              slice_start_at=None, slice_end_at=None):
        audio_clips = []
        if slice_start_at is None:
            slice_start_at = 0
        if slice_end_at is None:
            slice_end_at = self.duration

        for shape_line in self.shape_time_lines:
            shape = shape_line.shape

            #go deeper leve of internal timeline
            if shape_line.prop_time_lines.key_exists("internal"):
                prop_line = shape_line.prop_time_lines["internal"]
                t = 0
                for time_slice in prop_line.time_slices:
                    if time_slice.prop_data and time_slice.prop_data.get("type") == "timeline":
                        next_timeline = shape.timelines.get(time_slice.prop_data.get("timeline"))
                    else:
                        next_timeline = None
                    if next_timeline and t+time_slice.duration>slice_start_at and t<=slice_end_at:
                        tm_start = max(slice_start_at, t)
                        tm_end = min(t+time_slice.duration, slice_end_at)

                        lscale = (time_slice.end_value-time_slice.start_value)
                        lscale *= next_timeline.duration/time_slice.duration

                        pre_shift_time = time_slice.start_value*next_timeline.duration

                        next_slice_start_at = pre_shift_time + (tm_start-t)*lscale
                        next_slice_end_at = pre_shift_time + (tm_end-t)*lscale

                        audio_clips.extend(
                            next_timeline.get_audio_clips(
                                abs_time_offset=abs_time_offset+(tm_start-slice_start_at)/pre_scale,
                                pre_scale=lscale*pre_scale,
                                slice_start_at=next_slice_start_at,
                                slice_end_at=next_slice_end_at
                            )
                        )
                    t += time_slice.duration
                    if t>=slice_end_at:
                        break

            if not shape_line.prop_time_lines.key_exists("time_pos"):
                continue

            has_audio = (hasattr(shape, "audio_active") and shape.audio_active)
            prop_line = shape_line.prop_time_lines["time_pos"]

            if not has_audio:
                t = 0
                #go deeper level of document_shape
                for time_slice in prop_line.time_slices:
                    if not time_slice.prop_data:
                        continue
                    time_line_name = time_slice.prop_data.get("time_line_name")
                    if not time_line_name:
                        continue

                    next_timeline = shape.get_time_line_for(
                        time_slice.prop_data.get("document_path"),
                        time_line_name
                    )
                    if not next_timeline:
                        continue

                    if next_timeline and t+time_slice.duration>slice_start_at and t<=slice_end_at:
                        tm_start = max(slice_start_at, t)
                        tm_end = min(t+time_slice.duration, slice_end_at)

                        pre_shift_time = time_slice.start_value
                        lscale = (time_slice.end_value-time_slice.start_value)/time_slice.duration

                        audio_clips.extend(
                            next_timeline.get_audio_clips(
                                abs_time_offset=abs_time_offset+(tm_start-slice_start_at)/pre_scale,
                                pre_scale=lscale*pre_scale,
                                slice_start_at=(tm_start-t)*lscale+pre_shift_time,
                                slice_end_at=(tm_end-t)*lscale+pre_shift_time
                            )
                        )
                    t += time_slice.duration
                    if t>=slice_end_at:
                        break

            else:#get audio clips
                t = 0
                for time_slice in prop_line.time_slices:
                    if t+time_slice.duration>slice_start_at and t<=slice_end_at:
                        tm_start = max(slice_start_at, t)
                        tm_end = min(t+time_slice.duration, slice_end_at)

                        scale = (time_slice.end_value-time_slice.start_value)/time_slice.duration
                        scale *= pre_scale
                        duration = (tm_end-tm_start)/pre_scale

                        clip = AudioClipGenerator(
                            time_offset=abs_time_offset+(tm_start-slice_start_at)/pre_scale,
                            slice_offset=max(0, slice_start_at-t),
                            scale=scale,
                            duration=duration,
                            time_slice=time_slice
                        )
                        clip = clip.set_start(clip.time_offset)
                        audio_clips.append(clip)

                    t += time_slice.duration
                    if t>=slice_end_at:
                        break
        return audio_clips

    def sync_time_slices_with_time_marker(self, time_marker, prop_time_line=None):
        if isinstance(time_marker, str):
            time_marker = self.get_time_marker_by_text(time_marker)
            if not time_marker:
                return

        time_markers = self.get_time_markers_after(time_marker)
        time_markers.insert(0, time_marker)

        if prop_time_line:
            prop_time_line.sync_time_slices_with_time_markers(time_markers)
        else:
            for shape_time_line in self.shape_time_lines:
                shape_time_line.sync_time_slices_with_time_markers(time_markers)
