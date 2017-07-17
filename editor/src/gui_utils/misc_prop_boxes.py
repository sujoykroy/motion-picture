from shape_prop_box import *

class CommonShapePropBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback, shape_name_checker, insert_time_slice_callback):    
        ShapePropBox.__init__(self, parent_window, draw_callback,
                                shape_name_checker, insert_time_slice_callback)
        self.add_prop("name", PROP_TYPE_NAME_ENTRY)
        self.add_prop("show_points", PROP_TYPE_CHECK_BUTTON, can_insert_slice=False)
        self.add_prop("moveable", PROP_TYPE_CHECK_BUTTON, can_insert_slice=False)
        self.add_prop("selectable", PROP_TYPE_CHECK_BUTTON, can_insert_slice=False)
        self.add_prop("masked", PROP_TYPE_CHECK_BUTTON)
        self.add_prop("visible", PROP_TYPE_CHECK_BUTTON)
        self.add_prop("locked_to", PROP_TYPE_TEXT)
        self.add_prop("renderable", PROP_TYPE_CHECK_BUTTON, can_insert_slice=False)
        #self.add_prop("stage_xy", PROP_TYPE_POINT, None)

        self.add_prop("x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1), related=["xy"])
        self.add_prop("y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1), related=["xy"])
        self.add_prop("xy", PROP_TYPE_POINT, None, related=["x", "y"])
        self.add_prop("translation", PROP_TYPE_POINT,
                    dict(editable=False), can_insert_slice=False)
        self.add_prop("scale_x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-100, upper=100, step_increment=.10), related=["scale_y"])
        self.add_prop("scale_y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-100, upper=100, step_increment=.01), related=["scale_x"])
        self.add_prop("same_xy_scale", PROP_TYPE_CHECK_BUTTON, None, related=["scale_x", "scale_y"])
        self.add_prop("anchor_x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("anchor_y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("post_scale_x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-100, upper=100, step_increment=.10, page_increment=.1, page_size=1))
        self.add_prop("post_scale_y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-100, upper=100, step_increment=.01, page_increment=.1, page_size=1))
        self.add_prop("border_width", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=1000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("border_dash", PROP_TYPE_TEXT, None, can_insert_slice=False)
        self.add_prop("border_color", PROP_TYPE_COLOR, None)
        self.add_prop("fill_color", PROP_TYPE_COLOR, None)

        self.add_prop("width", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=1, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("height", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=1, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("angle", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-360, upper=360*100, step_increment=1, page_increment=1, page_size=1))
        mirror_comobobox = self.add_prop("mirror", PROP_TYPE_TEXT_LIST, None)
        mirror_options = [["None", 0], ["X", -1], ["Y", -2], ["XY", -3]]
        mirror_options.extend([["All", -4], ["Angle", -10]])
        mirror_comobobox.build_and_set_model(mirror_options)
        self.add_prop("mirror_angle", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=361, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("followed_upto", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=1, step_increment=.01))

    def insert_slice_button_clicked(self, widget, prop_name):
        if prop_name == "followed_upto":
            if self.prop_object != None:
                prop_data = dict(follow_curve="", follow_angle=False)
                self.insert_time_slice_callback(self.prop_object, prop_name, 0, 1, prop_data)
        else:
            super(CommonShapePropBox, self).insert_slice_button_clicked(widget, prop_name)

class RectangleShapePropBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, parent_window, draw_callback, None, insert_time_slice_callback)
        self.add_prop("corner_radius", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=1000, step_increment=1, page_increment=1, page_size=1))

class OvalShapePropBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, parent_window, draw_callback, None, insert_time_slice_callback)
        self.add_prop("sweep_angle", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-360, upper=361, step_increment=1, page_increment=1, page_size=1))

class RingShapePropBox(OvalShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        OvalShapePropBox.__init__(self, parent_window, draw_callback, insert_time_slice_callback)
        self.add_prop("thickness", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=1.01,
                     step_increment=.01, page_increment=.01, page_size=.01))

class CameraShapePropBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, parent_window, draw_callback, None, insert_time_slice_callback)
        aspect_ratio_combobox = self.add_prop("aspect_ratio", PROP_TYPE_TEXT_LIST, None)
        aspect_ratio_combobox.build_and_set_model(["16:9", "4:3", "16:10", "1:1"])
        eye_type_combobox = self.add_prop("eye_type", PROP_TYPE_TEXT_LIST, None)
        eye_type_combobox.build_and_set_model([["Rectangle", 0], ["Oval", 1]])

class TextShapePropBox(OvalShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        OvalShapePropBox.__init__(self, parent_window, draw_callback, insert_time_slice_callback)
        xalign_combobox = self.add_prop("x_align", PROP_TYPE_TEXT_LIST, None)
        yalign_combobox = self.add_prop("y_align", PROP_TYPE_TEXT_LIST, None)
        self.add_prop("font", PROP_TYPE_FONT, None)
        self.add_prop("font_color", PROP_TYPE_COLOR, None)
        linenalign_combobox = self.add_prop("line_align", PROP_TYPE_TEXT_LIST, None)
        self.add_prop("text", PROP_TYPE_LONG_TEXT, None)
        self.add_prop("exposure", PROP_TYPE_NUMBER_ENTRY,
            dict(value=0, lower=0, upper=2., step_increment=.01, page_increment=.1, page_size=.1))
        self.add_prop("char_width", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-1, upper=1000, step_increment=1, page_increment=1, page_size=1))

        xalign_combobox.build_and_set_model([["Left", 0], ["Center", 1], ["Right", 2]])
        yalign_combobox.build_and_set_model([["Top", 0], ["Middle", 1], ["Bottom", 2]])
        linenalign_combobox.build_and_set_model([["Left", 0], ["Center", 1], ["Right", 2]])

    def insert_slice_button_clicked(self, widget, prop_name):
        if prop_name == "exposure":
            if self.prop_object != None:
                value = self.prop_object.get_prop_value_for_time_slice(prop_name)
                prop_data = dict(text="")
                self.insert_time_slice_callback(self.prop_object, prop_name, value, value, prop_data)
        else:
            super(TextShapePropBox, self).insert_slice_button_clicked(widget, prop_name)

class MultiShapePropBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, parent_window, draw_callback, None, insert_time_slice_callback)
        self.poses_combo_box= self.add_prop("pose", PROP_TYPE_IMAGE_LIST, None)
        self.timelines_combo_box= self.add_prop("timeline", PROP_TYPE_TEXT_LIST, None)
        self.add_prop("imported_from", PROP_TYPE_TEXT)

    def set_prop_object(self, prop_object):
        ShapePropBox.set_prop_object(self, prop_object)
        self.poses_combo_box.build_and_set_model(prop_object.get_pose_list())
        self.timelines_combo_box.build_and_set_model(prop_object.get_timelines_model())

    def has_prop(self, prop_name):
        if prop_name in ("pose", "timeline"):
            return True
        return self.prop_object.has_prop(prop_name)

    def insert_slice_button_clicked(self, widget, prop_name):
        if self.prop_object is None: return
        if prop_name == "pose":
            start_pose = self.poses_combo_box.get_value()
            prop_data = dict(start_pose=start_pose, end_pose=None, type="pose")
        elif prop_name == "timeline":
            timeline = self.timelines_combo_box.get_value()
            pose = self.poses_combo_box.get_value()
            #if not pose: return
            prop_data = dict(pose=pose, timeline=timeline, type="timeline")

        self.insert_time_slice_callback(self.prop_object, "internal" , 0, 1, prop_data)

class ImageShapePropBox(RectangleShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        RectangleShapePropBox.__init__(self, parent_window, draw_callback, self.new_insert_time_slice)
        self.add_prop("image_path", PROP_TYPE_FILE, dict(file_type=[["Image", "image/*"]]))
        self.add_prop("alpha", PROP_TYPE_NUMBER_ENTRY, dict(value=1, lower=0, upper=1, step_increment=.1))
        self.orig_insert_time_slice_callback = insert_time_slice_callback

    def new_insert_time_slice(self, shape, prop_name, start_value, end_value=None, prop_data=None):
        if prop_name == "alpha":
            prop_data = dict(image_path="")
        self.orig_insert_time_slice_callback(shape, prop_name, start_value, end_value, prop_data)


class AVShapePropBox(RectangleShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        RectangleShapePropBox.__init__(self, parent_window, draw_callback, self.new_insert_time_slice)
        self.add_prop("time_pos", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=3*60*60, step_increment=.01))
        self.orig_insert_time_slice_callback = insert_time_slice_callback
        self.path_name = None

    def new_insert_time_slice(self, shape, prop_name, start_value, end_value=None, prop_data=None):
        if prop_name == "time_pos":
            start_value = 0
            end_value = self.prop_object.get_duration()
            duration = self.prop_object.get_duration()
            prop_data = {self.path_name:self.prop_object.get_av_filename()}
        else:
            duration = None
        self.orig_insert_time_slice_callback(shape, prop_name, start_value, end_value, prop_data, duration)

class AudioShapePropBox(AVShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        AVShapePropBox.__init__(self, parent_window, draw_callback, insert_time_slice_callback)
        self.add_prop("audio_path", PROP_TYPE_FILE, dict(file_type=[["Audio", "audio/*"], ["Video", "video/*"]]))
        self.add_prop("audio_length", PROP_TYPE_LABEL)
        self.add_prop("audio_active", PROP_TYPE_CHECK_BUTTON, can_insert_slice=False)
        self.path_name = "audio_path"

class VideoShapePropBox(AVShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        AVShapePropBox.__init__(self, parent_window, draw_callback, insert_time_slice_callback)
        self.add_prop("video_length", PROP_TYPE_LABEL)
        self.add_prop("video_path", PROP_TYPE_FILE, dict(file_type=[["Video", "video/*"]]))
        self.add_prop("use_thread", PROP_TYPE_CHECK_BUTTON, can_insert_slice=False)
        self.add_prop("audio_active", PROP_TYPE_CHECK_BUTTON, can_insert_slice=False)
        self.path_name = "video_path"

class CurvePointGroupShapePropBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, parent_window, draw_callback, None, insert_time_slice_callback)
        self.add_prop("show_anchor", PROP_TYPE_CHECK_BUTTON, None, can_insert_slice=False)

class CustomShapePropBox(RectangleShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        RectangleShapePropBox.__init__(self, parent_window, draw_callback, insert_time_slice_callback)
        self.add_prop("progress", PROP_TYPE_NUMBER_ENTRY,
                dict(step_increment=.01, value=0, lower=0, upper=1))
        self.add_prop("code_path", PROP_TYPE_FILE, dict(file_type=[["Python", "*.py"]]))
        self.add_prop("params", PROP_TYPE_LONG_TEXT)

class DocumentShapePropBox(RectangleShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        RectangleShapePropBox.__init__(self, parent_window, draw_callback, self.new_insert_time_slice)
        self.add_prop("time_line_length", PROP_TYPE_LABEL)
        self.add_prop("document_path", PROP_TYPE_FILE, dict(file_type=[["Document", "*.xml"]]))
        self.add_prop("time_line_name", PROP_TYPE_TEXT)
        self.add_prop("camera", PROP_TYPE_TEXT)
        self.add_prop("time_pos", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=3*60*60, step_increment=.01))
        self.orig_insert_time_slice_callback = insert_time_slice_callback
        self.path_name = None

    def new_insert_time_slice(self, shape, prop_name, start_value, end_value=None, prop_data=None):
        if prop_name == "time_pos":
            start_value = 0
            end_value = self.prop_object.get_duration()
            duration = self.prop_object.get_duration()
            prop_data = dict(
                document_path=self.prop_object.document_path,
                time_line_name="",
                camera=""
            )
        else:
            duration = None
        self.orig_insert_time_slice_callback(shape, prop_name, start_value, end_value, prop_data, duration)


class ThreeDShapePropBox(RectangleShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        RectangleShapePropBox.__init__(self, parent_window, draw_callback, self.new_insert_time_slice)
        self.add_prop("camera_rotate_x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-3*60*6, upper=3*60*60, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("camera_rotate_y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-3*60*6, upper=3*60*60, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("camera_rotate_z", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-3*60*6, upper=3*60*60, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("object_scale", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100000, step_increment=1))
        self.add_prop("quality_scale", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0.01, lower=.001, upper=10, step_increment=.01, digits=3))
        """
        self.add_prop("viewer_z", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=100000, step_increment=1))
        self.add_prop("camera_position_z", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=100000, step_increment=1))
        """
        self.add_prop("wire_color", PROP_TYPE_COLOR, None)
        self.add_prop("wire_width", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=1000, step_increment=.1))
        self.add_prop("high_quality", PROP_TYPE_CHECK_BUTTON, None)
        self.add_prop("filepath", PROP_TYPE_FILE, dict(file_type=[["Collada", "*.dae"]]))
        self.add_prop("item_names", PROP_TYPE_TEXT)
        self.orig_insert_time_slice_callback = insert_time_slice_callback

    def new_insert_time_slice(self, shape, prop_name, start_value, end_value=None, prop_data=None):
        if prop_name == "time_pos":
            start_value = 0
            end_value = self.prop_object.get_duration()
            duration = self.prop_object.get_duration()
            prop_data = dict(av_filename=self.prop_object.get_av_filename())
        else:
            duration = None
        self.orig_insert_time_slice_callback(shape, prop_name, start_value, end_value, prop_data, duration)

class CustomPropsBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback,
                       insert_time_slice_callback, edit_callback, shape):
        ShapePropBox.__init__(self, parent_window, draw_callback, None, insert_time_slice_callback)
        self.edit_callback = edit_callback
        if not shape.custom_props:
            return
        for custom_prop in shape.custom_props.props:
            prop_name = custom_prop.prop_name
            prop_type_name = custom_prop.get_prop_type_name()
            if prop_type_name == "number":
                self.add_prop(
                    prop_name, PROP_TYPE_NUMBER_ENTRY,
                    dict(value=0, lower=-1000., upper=1000.,
                        step_increment=.1, page_increment=.1, page_size=.1))
            elif prop_type_name == "point":
                self.add_prop(prop_name, PROP_TYPE_POINT, None)
            elif prop_type_name == "text":
                self.add_prop(prop_name, PROP_TYPE_TEXT, None, can_insert_slice=False)
            elif prop_type_name == "font":
                self.add_prop(prop_name, PROP_TYPE_FONT, None, can_insert_slice=False)
            elif prop_type_name == "color":
                self.add_prop(prop_name, PROP_TYPE_COLOR, None, can_insert_slice=False)

        self.set_prop_object(shape)

    def add_prop(self, prop_name, value_type, values, can_insert_slice = True):
        prop_widget = super(CustomPropsBox, self).add_prop(
                prop_name, value_type, values, can_insert_slice)
        edit_button = Gtk.Button("E")
        edit_button.connect("clicked", self.edit_button_clicked, prop_name)
        widgets = self.widget_rows[-1]
        widgets.append(edit_button)

    def edit_button_clicked(self, widget, prop_name):
        self.edit_callback(prop_name)
