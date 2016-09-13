from shape_prop_box import *

class CommonShapePropBox(ShapePropBox):
    def __init__(self, draw_callback, shape_name_checker, insert_time_slice_callback):
        ShapePropBox.__init__(self, draw_callback, shape_name_checker, insert_time_slice_callback)
        self.add_prop("name",  PROP_TYPE_NAME_ENTRY, None)
        self.add_prop("stage_xy",  PROP_TYPE_POINT, None)

        self.add_prop("x",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("y",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("scale_x",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100, step_increment=.10, page_increment=.1, page_size=1))
        self.add_prop("scale_y",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100, step_increment=.01, page_increment=.1, page_size=1))
        self.add_prop("anchor_x",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("anchor_y",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-10000, upper=10000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("post_scale_x",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100, step_increment=.10, page_increment=.1, page_size=1))
        self.add_prop("post_scale_y",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=.001, upper=100, step_increment=.01, page_increment=.1, page_size=1))
        self.add_prop("border_width",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=1, upper=1000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("border_color",  PROP_TYPE_COLOR, None)
        self.add_prop("fill_color",  PROP_TYPE_COLOR, None)

        self.add_prop("width",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=1, upper=1000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("height",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=1, upper=1000, step_increment=1, page_increment=1, page_size=1))
        self.add_prop("angle",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-360, upper=360*100, step_increment=1, page_increment=1, page_size=1))

class RectangleShapePropBox(ShapePropBox):
    def __init__(self, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, draw_callback, None, insert_time_slice_callback)
        self.add_prop("corner_radius",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=1, upper=1000, step_increment=1, page_increment=1, page_size=1))

class OvalShapePropBox(ShapePropBox):
    def __init__(self, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, draw_callback, None, insert_time_slice_callback)
        self.add_prop("sweep_angle",  PROP_TYPE_NUMBER_ENTRY,
                dict(value=0, lower=-360, upper=361, step_increment=1, page_increment=1, page_size=1))

class MultiShapePropBox(ShapePropBox):
    def __init__(self, draw_callback, insert_time_slice_callback):
        ShapePropBox.__init__(self, draw_callback, None, insert_time_slice_callback)
        self.poses_combo_box= self.add_prop("pose",  PROP_TYPE_TEXT_LIST, None)
        self.timelines_combo_box= self.add_prop("timeline",  PROP_TYPE_TEXT_LIST, None)

    def set_prop_object(self, prop_object):
        ShapePropBox.set_prop_object(self, prop_object)
        self.poses_combo_box.build_and_set_model(sorted(prop_object.poses.keys()))
        self.timelines_combo_box.build_and_set_model(sorted(prop_object.timelines.keys()))

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

