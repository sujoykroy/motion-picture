from gi.repository import Gtk
from name_value_combo_box import NameValueComboBox
from text_input_dialog import TextInputDialog

class MultiShapeInternalPropBox(Gtk.VBox):
    def __init__(self, draw_callback, timeline_load_callback):
        Gtk.VBox.__init__(self)
        self.draw_callback = draw_callback
        self.timeline_load_callback = timeline_load_callback

        pose_label = Gtk.Label("Poses")
        self.poses_combo_box = NameValueComboBox()
        self.poses_combo_box.connect("changed", self.poses_combo_box_changed)
        self.apply_pose_button = Gtk.Button("Apply")
        self.apply_pose_button.connect("clicked", self.apply_pose_button_clicked)
        self.new_pose_button = Gtk.Button("New")
        self.new_pose_button.connect("clicked", self.new_pose_button_clicked)
        self.rename_pose_button = Gtk.Button("Rename")
        self.rename_pose_button.connect("clicked", self.rename_pose_button_clicked)
        self.save_pose_button = Gtk.Button("Save")
        self.save_pose_button.connect("clicked", self.save_pose_button_clicked)

        pose_button_box = Gtk.HBox()
        pose_button_box.pack_start(self.apply_pose_button, expand=False, fill=False, padding=0)
        pose_button_box.pack_start(self.save_pose_button, expand=False, fill=False, padding=0)
        pose_button_box.pack_start(self.rename_pose_button, expand=False, fill=False, padding=0)
        pose_button_box.pack_start(self.new_pose_button, expand=False, fill=False, padding=0)

        self.pack_start(pose_label, expand=False, fill=False, padding=0)
        self.pack_start(self.poses_combo_box, expand=False, fill=False, padding=0)
        self.pack_start(pose_button_box, expand=False, fill=False, padding=0)

        timeline_label = Gtk.Label("TimeLines")
        self.timelines_combo_box = NameValueComboBox()
        self.timelines_combo_box.connect("changed", self.timelines_combo_box_changed)
        self.show_timeline_button = Gtk.Button("Show")
        self.show_timeline_button.connect("clicked", self.show_timeline_button_clicked)
        self.new_timeline_button = Gtk.Button("New")
        self.new_timeline_button.connect("clicked", self.new_timeline_button_clicked)
        self.rename_timeline_button = Gtk.Button("Rename")
        self.rename_timeline_button.connect("clicked", self.rename_timeline_button_clicked)

        timeline_button_box = Gtk.HBox()
        timeline_button_box.pack_start(self.show_timeline_button, expand=False, fill=False, padding=0)
        timeline_button_box.pack_start(self.rename_timeline_button, expand=False, fill=False, padding=0)
        timeline_button_box.pack_start(self.new_timeline_button, expand=False, fill=False, padding=0)

        self.pack_start(timeline_label, expand=False, fill=False, padding=0)
        self.pack_start(self.timelines_combo_box, expand=False, fill=False, padding=0)
        self.pack_start(timeline_button_box, expand=False, fill=False, padding=0)

        self.multi_shape = None

    def set_multi_shape(self, multi_shape):
        self.multi_shape = multi_shape
        self.apply_pose_button.hide()
        self.rename_pose_button.hide()
        self.save_pose_button.hide()
        self.show_timeline_button.hide()
        self.rename_timeline_button.hide()
        self.update(poses=True, timelines=True)

    def update(self, poses=False, timelines=False):
        if poses:
            self.poses_combo_box.build_and_set_model(sorted(self.multi_shape.poses.keys()))
        if timelines:
            self.timelines_combo_box.build_and_set_model(sorted(self.multi_shape.timelines.keys()))

    def poses_combo_box_changed(self, widget):
        pose_name = self.poses_combo_box.get_value()
        if pose_name:
            self.apply_pose_button.show()
            self.save_pose_button.show()
            self.rename_pose_button.show()
        else:
            self.apply_pose_button.hide()
            self.save_pose_button.hide()
            self.rename_pose_button.hide()

    def timelines_combo_box_changed(self, widget):
        timeline_name = self.timelines_combo_box.get_value()
        if timeline_name:
            self.show_timeline_button.show()
            self.rename_timeline_button.show()
        else:
            self.show_timeline_button.hide()
            self.rename_timeline_button.hide()

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
        timeline = self.multi_shape.get_new_timeline()
        self.update(timelines=True)
        self.timelines_combo_box.set_value(timeline.name)

    def rename_pose_button_clicked(self, widget):
        pose_name = self.poses_combo_box.get_value()
        dialog = TextInputDialog(self.parent_window,
                "Rename pose", "Rename the pose [{0}] to, -".format(pose_name))
        if dialog.run() == Gtk.ResponseType.OK:
            new_pose_name = dialog.get_input_text().strip()
            if new_pose_name and self.multi_shape.rename_pose(pose_name, new_pose_name):
                self.update(poses=True)
                self.poses_combo_box.set_value(new_pose_name)
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

    def save_pose_button_clicked(self, widget):
        pose_name = self.poses_combo_box.get_value()
        if pose_name:
            self.multi_shape.save_pose(pose_name)

