from gi.repository import Gtk
from name_value_combo_box import NameValueComboBox
import buttons

class InteriorPoseBox(object):
    def __init__(self, insert_time_slice_callback):
        self.insert_time_slice_callback = insert_time_slice_callback

        self.label = Gtk.Label("Add Interior Pose")
        self.label.set_halign(Gtk.Align.START)
        self.pose_name_entry = Gtk.Entry()
        self.add_button = buttons.create_new_image_button("insert_time_slice", size=16)
        self.add_button.connect("clicked", self.add_button_clicked)
        self.shape = None

    def set_shape(self, shape):
        self.shape = shape

    def add_button_clicked(self, widget):
        pose_name = self.pose_name_entry.get_text().strip()
        if not pose_name:
            return
        self.insert_time_slice_callback(
            shape=self.shape,
            prop_name="pose_" + pose_name,
            start_value=0.,
            end_value=1.,
            prop_data=dict(shape="", start_pose="", end_pose="", type="pose"))

    def hide(self):
        self.label.hide()
        self.pose_name_entry.hide()
        self.add_button.hide()

    def show(self):
        self.label.show()
        self.pose_name_entry.show()
        self.add_button.show()
