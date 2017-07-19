from gi.repository import Gtk
from name_value_combo_box import NameValueComboBox
from image_combo_box import ImageComboBox
from helper_dialogs import TextInputDialog, YesNoDialog
from ..time_lines import MultiShapeTimeLine
from buttons import *

class MultiShapeInternalPropBox(Gtk.VBox):
    def __init__(self, draw_callback, timeline_load_callback, insert_time_slice_callback):
        Gtk.VBox.__init__(self)
        self.set_margin_left(10)
        self.set_margin_right(10)

        self.draw_callback = draw_callback
        self.timeline_load_callback = timeline_load_callback
        self.insert_time_slice_callback = insert_time_slice_callback

        pose_label = Gtk.Label("Poses")
        self.poses_combo_box = ImageComboBox()
        self.poses_combo_box.connect("changed", self.poses_combo_box_changed)
        self.apply_pose_button = create_new_image_button("apply")
        self.apply_pose_button.connect("clicked", self.apply_pose_button_clicked)
        self.new_pose_button = create_new_image_button("new")
        self.new_pose_button.connect("clicked", self.new_pose_button_clicked)
        self.rename_pose_button = create_new_image_button("rename")
        self.rename_pose_button.connect("clicked", self.rename_pose_button_clicked)
        self.delete_pose_button = create_new_image_button("delete")
        self.delete_pose_button.connect("clicked", self.delete_pose_button_clicked)
        self.save_pose_button = create_new_image_button("save")
        self.save_pose_button.connect("clicked", self.save_pose_button_clicked)
        self.insert_pose_button = create_new_image_button("insert_time_slice")
        self.insert_pose_button.connect("clicked", self.insert_slice_button_clicked, "pose")

        pose_button_box = Gtk.HBox()
        pose_button_box.pack_start(self.apply_pose_button, expand=False, fill=False, padding=0)
        pose_button_box.pack_start(self.save_pose_button, expand=False, fill=False, padding=0)
        pose_button_box.pack_start(self.rename_pose_button, expand=False, fill=False, padding=0)
        pose_button_box.pack_start(self.delete_pose_button, expand=False, fill=False, padding=0)
        pose_button_box.pack_start(self.new_pose_button, expand=False, fill=False, padding=0)
        pose_button_box.pack_start(self.insert_pose_button, expand=False, fill=False, padding=0)

        self.pack_start(pose_label, expand=False, fill=False, padding=0)
        self.pack_start(self.poses_combo_box, expand=False, fill=False, padding=0)
        self.pack_start(pose_button_box, expand=False, fill=False, padding=0)

        timeline_label = Gtk.Label("TimeLines")
        self.timelines_combo_box = NameValueComboBox()
        self.timelines_combo_box.connect("changed", self.timelines_combo_box_changed)
        self.show_timeline_button = create_new_image_button("show_time_line")
        self.show_timeline_button.connect("clicked", self.show_timeline_button_clicked)
        self.new_timeline_button = create_new_image_button("new")
        self.new_timeline_button.connect("clicked", self.new_timeline_button_clicked)
        self.rename_timeline_button =  create_new_image_button("rename")
        self.rename_timeline_button.connect("clicked", self.rename_timeline_button_clicked)
        self.delete_timeline_button = create_new_image_button("delete")
        self.delete_timeline_button.connect("clicked", self.delete_timeline_button_clicked)
        self.insert_time_line_button = create_new_image_button("insert_time_slice")
        self.insert_time_line_button.connect("clicked", self.insert_slice_button_clicked, "timeline")
        self.insert_time_line_internal_button = create_new_image_button(
                    "insert_time_slice_internal",
                    desc="Insert New Internal Time Slice")
        self.insert_time_line_internal_button.connect(
                "clicked", self.insert_slice_button_clicked, "timeline_internal")

        timeline_button_box = Gtk.HBox()
        timeline_button_box.pack_start(self.show_timeline_button, expand=False, fill=False, padding=0)
        timeline_button_box.pack_start(self.rename_timeline_button, expand=False, fill=False, padding=0)
        timeline_button_box.pack_start(self.delete_timeline_button, expand=False, fill=False, padding=0)
        timeline_button_box.pack_start(self.new_timeline_button, expand=False, fill=False, padding=0)
        timeline_button_box.pack_start(self.insert_time_line_button, expand=False, fill=False, padding=0)
        timeline_button_box.pack_start(self.insert_time_line_internal_button, expand=False, fill=False, padding=0)

        self.pack_start(timeline_label, expand=False, fill=False, padding=0)
        self.pack_start(self.timelines_combo_box, expand=False, fill=False, padding=0)
        self.pack_start(timeline_button_box, expand=False, fill=False, padding=0)

        self.multi_shape = None

    def set_multi_shape(self, multi_shape):
        self.multi_shape = multi_shape
        self.apply_pose_button.hide()
        self.rename_pose_button.hide()
        self.save_pose_button.hide()
        self.delete_pose_button.hide()
        self.insert_pose_button.hide()

        self.show_timeline_button.hide()
        self.rename_timeline_button.hide()
        self.delete_timeline_button.hide()
        self.insert_time_line_button.hide()
        self.insert_time_line_internal_button.hide()
        self.update(poses=True, timelines=True)

    def update(self, poses=False, timelines=False):
        if poses:
            self.poses_combo_box.build_and_set_model(self.multi_shape.get_pose_list())
            self.poses_combo_box_changed(widget=None)
            self.poses_combo_box.set_value(self.multi_shape.pose)
        if timelines:
            self.timelines_combo_box.build_and_set_model(sorted(self.multi_shape.timelines.keys()))
            self.timelines_combo_box_changed(widget=None)

    def poses_combo_box_changed(self, widget):
        pose_name = self.poses_combo_box.get_value()
        if pose_name:
            self.apply_pose_button.show()
            self.save_pose_button.show()
            self.rename_pose_button.show()
            self.delete_pose_button.show()
            self.insert_pose_button.show()
        else:
            self.apply_pose_button.hide()
            self.save_pose_button.hide()
            self.rename_pose_button.hide()
            self.delete_pose_button.hide()
            self.insert_pose_button.hide()

    def set_timeline(self, timeline_name):
        self.timelines_combo_box.set_value(timeline_name)

    def timelines_combo_box_changed(self, widget):
        timeline_name = self.timelines_combo_box.get_value()
        if timeline_name:
            self.show_timeline_button.show()
            self.rename_timeline_button.show()
            self.delete_timeline_button.show()
            self.insert_time_line_button.show()
            self.insert_time_line_button.show()
        else:
            self.show_timeline_button.hide()
            self.rename_timeline_button.hide()
            self.delete_timeline_button.hide()
            self.insert_time_line_button.hide()
            self.insert_time_line_button.hide()

    def apply_pose_button_clicked(self, widget):
        pose_name = self.poses_combo_box.get_value()
        if pose_name:
            self.multi_shape.set_pose(pose_name)
            self.draw_callback()

    def show_timeline_button_clicked(self, widget):
        timeline_name = self.timelines_combo_box.get_value()
        if timeline_name:
            self.timeline_load_callback(self.multi_shape.timelines[timeline_name])

    def new_pose_button_clicked(self, widget):
        pose_name = self.multi_shape.save_pose(None)
        self.update(poses=True)
        self.poses_combo_box.set_value(pose_name)

    def new_timeline_button_clicked(self, widget):
        timeline = self.multi_shape.get_new_timeline(MultiShapeTimeLine)
        self.update(timelines=True)
        self.timelines_combo_box.set_value(timeline.name)

    def rename_pose_button_clicked(self, widget):
        pose_name = self.poses_combo_box.get_value()
        dialog = TextInputDialog(self.parent_window,
                "Rename pose", "Rename the pose [{0}] to, -".format(pose_name),
                input_text=pose_name)
        if dialog.run() == Gtk.ResponseType.OK:
            new_pose_name = dialog.get_input_text().strip()
            if new_pose_name and self.multi_shape.rename_pose(pose_name, new_pose_name):
                self.update(poses=True)
                self.poses_combo_box.set_value(new_pose_name)
        dialog.destroy()

    def delete_pose_button_clicked(self, widget):
        pose_name = self.poses_combo_box.get_value()
        dialog = YesNoDialog(self.parent_window,
                "Delete Pose", "Do you really want to delete Pose [{0}]".format(pose_name))
        if dialog.run() == Gtk.ResponseType.YES:
            self.multi_shape.delete_pose(pose_name)
            self.update(poses=True)
        dialog.destroy()

    def rename_timeline_button_clicked(self, widget):
        timeline_name = self.timelines_combo_box.get_value()
        dialog = TextInputDialog(self.parent_window,
                "Rename timeline", "Rename the timeline [{0}] to, -".format(timeline_name))
        if dialog.run() == Gtk.ResponseType.OK:
            new_timeline_name = dialog.get_input_text().strip()
            if new_timeline_name and self.multi_shape.rename_timeline(timeline_name, new_timeline_name):
                self.update(timelines=True)
                self.timelines_combo_box.set_value(new_timeline_name)
        dialog.destroy()

    def delete_timeline_button_clicked(self, widget):
        timeline_name = self.timelines_combo_box.get_value()
        dialog = YesNoDialog(self.parent_window,
                "Delete Timeline", "Do you really want to delete Timeline [{0}]".format(timeline_name))
        if dialog.run() == Gtk.ResponseType.YES:
            self.multi_shape.delete_timeline(timeline_name)
            self.update(timelines=True)
        dialog.destroy()

    def save_pose_button_clicked(self, widget):
        pose_name = self.poses_combo_box.get_value()
        if pose_name:
            dialog = YesNoDialog(self.parent_window,
                "Save Pose", "Do you really want to overwrite Pose [{0}]".format(pose_name))
            if dialog.run() == Gtk.ResponseType.YES:
                self.multi_shape.save_pose(pose_name)
                self.update(poses=True)
            dialog.destroy()

    def insert_slice_button_clicked(self, widget, prop_name):
        if prop_name == "pose":
            start_pose = self.poses_combo_box.get_value()
            if start_pose:
                prop_data = dict(start_pose=start_pose, end_pose=None, type="pose")
                self.insert_time_slice_callback(self.multi_shape, "internal" , 0, 1, prop_data)
        elif prop_name == "timeline":
            timeline_name = self.timelines_combo_box.get_value()
            if timeline_name:
                self.insert_time_slice_callback(self.multi_shape, "tm_" +timeline_name , 0, 1)
        elif prop_name == "timeline_internal":
            timeline_name = self.timelines_combo_box.get_value()
            if timeline_name:
                prop_data = dict(timeline=timeline_name, pose="", type="timeline")
                self.insert_time_slice_callback(self.multi_shape, "internal" , 0, 1, prop_data)
