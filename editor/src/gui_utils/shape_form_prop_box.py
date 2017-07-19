from gi.repository import Gtk
from image_combo_box import ImageComboBox
from helper_dialogs import TextInputDialog, YesNoDialog
from buttons import *

class ShapeFormPropBox(object):
    def __init__(self, draw_callback, insert_time_slice_callback):
        self.draw_callback = draw_callback
        self.insert_time_slice_callback = insert_time_slice_callback
        self.form_label = Gtk.Label("Forms")
        self.forms_combo_box = ImageComboBox()
        self.forms_combo_box.connect("changed", self.forms_combo_box_changed)
        self.apply_form_button = create_new_image_button("apply")
        self.apply_form_button.connect("clicked", self.apply_form_button_clicked)
        self.new_form_button = create_new_image_button("new")
        self.new_form_button.connect("clicked", self.new_form_button_clicked)
        self.rename_form_button = create_new_image_button("rename")
        self.rename_form_button.connect("clicked", self.rename_form_button_clicked)
        self.delete_form_button = create_new_image_button("delete")
        self.delete_form_button.connect("clicked", self.delete_form_button_clicked)
        self.save_form_button = create_new_image_button("save")
        self.save_form_button.connect("clicked", self.save_form_button_clicked)

        self.form_button_box = Gtk.HBox()
        self.form_button_box.pack_start(self.apply_form_button, expand=False, fill=False, padding=0)
        self.form_button_box.pack_start(self.save_form_button, expand=False, fill=False, padding=0)
        self.form_button_box.pack_start(self.rename_form_button, expand=False, fill=False, padding=0)
        self.form_button_box.pack_start(self.delete_form_button, expand=False, fill=False, padding=0)
        self.form_button_box.pack_start(self.new_form_button, expand=False, fill=False, padding=0)

        self.insert_slice_button = create_new_image_button("insert_time_slice")
        self.insert_slice_button.connect("clicked", self.insert_slice_button_clicked)
        self.form_button_box.pack_start(self.insert_slice_button, expand=False, fill=False, padding=0)

        self.curve_shape = None

    def hide(self):
        self.form_label.hide()
        self.forms_combo_box.hide()
        self.form_button_box.hide()

    def show(self):
        self.form_label.show()
        self.forms_combo_box.show()
        self.form_button_box.show()

    def set_curve_shape(self, curve_shape):
        if self.curve_shape == curve_shape: return
        self.curve_shape = curve_shape
        self.apply_form_button.hide()
        self.rename_form_button.hide()
        self.save_form_button.hide()
        self.delete_form_button.hide()
        self.update()
        if self.curve_shape:
            self.forms_combo_box.set_value(self.curve_shape.get_prop_value("form_name"))

    def update(self):
        if self.curve_shape:
            values = self.curve_shape.get_form_list()
        else:
            values = None
        self.forms_combo_box.build_and_set_model(values)
        self.forms_combo_box_changed(widget=None)
        self.forms_combo_box.set_value(None)

    def forms_combo_box_changed(self, widget):
        form_name = self.forms_combo_box.get_value()
        if form_name:
            self.apply_form_button.show()
            self.rename_form_button.show()
            self.save_form_button.show()
            self.delete_form_button.show()
            self.insert_slice_button.show()
        else:
            self.apply_form_button.hide()
            self.rename_form_button.hide()
            self.save_form_button.hide()
            self.delete_form_button.hide()
            self.insert_slice_button.hide()

    def apply_form_button_clicked(self, widget):
        form_name = self.forms_combo_box.get_value()
        if form_name:
            self.curve_shape.set_form(form_name)
            self.draw_callback()

    def new_form_button_clicked(self, widget):
        form_name = self.curve_shape.save_form(None)
        self.update()
        self.forms_combo_box.set_value(form_name)

    def rename_form_button_clicked(self, widget):
        form_name = self.forms_combo_box.get_value()
        dialog = TextInputDialog(self.parent_window,
                "Rename form", "Rename the form [{0}] to, -".format(form_name),
                input_text=form_name)
        if dialog.run() == Gtk.ResponseType.OK:
            new_form_name = dialog.get_input_text().strip()
            if new_form_name and self.curve_shape.rename_form(form_name, new_form_name):
                self.update()
                self.forms_combo_box.set_value(new_form_name)
        dialog.destroy()

    def delete_form_button_clicked(self, widget):
        form_name = self.forms_combo_box.get_value()
        dialog = YesNoDialog(self.parent_window,
                "Delete Form", "Do you really want to delete Form [{0}]".format(form_name))
        if dialog.run() == Gtk.ResponseType.YES:
            self.curve_shape.delete_form(form_name)
            self.update()
        dialog.destroy()

    def save_form_button_clicked(self, widget):
        form_name = self.forms_combo_box.get_value()
        if form_name:
            dialog = YesNoDialog(self.parent_window,
                "Save Form", "Do you really want to overwrite Form [{0}]".format(form_name))
            if dialog.run() == Gtk.ResponseType.YES:
                self.curve_shape.save_form(form_name)
                self.update()
                self.forms_combo_box.set_value(form_name)
            dialog.destroy()

    def insert_slice_button_clicked(self, widget):
        form_name = self.forms_combo_box.get_value()
        if form_name:
            prop_data = dict(type="form", start_form=form_name, end_form=None)
            self.insert_time_slice_callback(self.curve_shape, "internal", 0., 1., prop_data)

