from shape_prop_box import *

class CommonShapePropBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback, shape_name_checker, insert_time_slice_callback):    
        ShapePropBox.__init__(self, parent_window, draw_callback,
                                shape_name_checker, insert_time_slice_callback)
        self.add_prop("name", PROP_TYPE_NAME_ENTRY, None)
        self.add_prop("show_points", PROP_TYPE_CHECK_BUTTON, None)
        self.add_prop("moveable", PROP_TYPE_CHECK_BUTTON, None)
        self.add_prop("masked", PROP_TYPE_CHECK_BUTTON, None)
        self.add_prop("stage_xy", PROP_TYPE_POINT, None)
        self.add_prop("alpha", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=1.1, step_increment=.1, page_increment=.1, page_size=.1))

        self.add_prop("x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("scale_x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100, step_increment=.10, page_increment=.1, page_size=1))
        self.add_prop("scale_y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100, step_increment=.01, page_increment=.1, page_size=1))
        self.add_prop("anchor_x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("anchor_y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("post_scale_x", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100, step_increment=.10, page_increment=.1, page_size=1))
        self.add_prop("post_scale_y", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100, step_increment=.01, page_increment=.1, page_size=1))
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

class MultiShapePropBox(ShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, parent_window, draw_callback, None, insert_time_slice_callback)
        self.poses_combo_box= self.add_prop("pose", PROP_TYPE_TEXT_LIST, None)
        self.timelines_combo_box= self.add_prop("timeline", PROP_TYPE_TEXT_LIST, None)

    def set_prop_object(self, prop_object):
        ShapePropBox.set_prop_object(self, prop_object)
        self.poses_combo_box.build_and_set_model(sorted(prop_object.poses.keys()))
        self.timelines_combo_box.build_and_set_model(sorted(prop_object.timelines.keys()))

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
            if not pose: return
            prop_data = dict(pose=pose, timeline=timeline, type="timeline")

        self.insert_time_slice_callback(self.prop_object, "internal" , 0, 1, prop_data)

class MovieShapePropBox(RectangleShapePropBox):
    def __init__(self, parent_window, draw_callback, insert_time_slice_callback):
        RectangleShapePropBox.__init__(self, parent_window, draw_callback, insert_time_slice_callback)
        self.add_prop("time_pos", PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=0, upper=1000, step_increment=1, page_increment=1, page_size=1))
