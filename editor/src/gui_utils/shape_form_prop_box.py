from gi.repository import Gtk
from name_value_combo_box import NameValueComboBox
from helper_dialogs import TextInputDialog

class ShapeFormPropBox(object):
    def __init__(self, draw_callback, insert_time_slice_callback):
        self.draw_callback = draw_callback
        self.insert_time_slice_callback = insert_time_slice_callback
        self.form_label = Gtk.Label("Forms")
        self.forms_combo_box = NameValueComboBox()
        self.forms_combo_box.connect("changed", self.forms_combo_box_changed)
        self.apply_form_button = Gtk.Button("Apply")
        self.apply_form_button.connect("clicked", self.apply_form_button_clicked)
        self.new_form_button = Gtk.Button("New")
        self.new_form_button.connect("clicked", self.new_form_button_clicked)
        self.rename_form_button = Gtk.Button("Rename")
        self.rename_form_button.connect("clicked", self.rename_form_button_clicked)
        self.save_form_button = Gtk.Button("Save")
        self.save_form_button.connect("clicked", self.save_form_button_clicked)

        self.form_button_box = Gtk.HBox()
        self.form_button_box.pack_start(self.apply_form_button, expand=False, fill=False, padding=0)
        self.form_button_box.pack_start(self.save_form_button, expand=False, fill=False, padding=0)
        self.form_button_box.pack_start(self.rename_form_button, expand=False, fill=False, padding=0)
        self.form_button_box.pack_start(self.new_form_button, expand=False, fill=False, padding=0)


        insert_slice_button = Gtk.Button("[+]")
        insert_slice_button.connect("clicked", self.insert_slice_button_clicked)
        self.form_button_box.pack_start(insert_slice_button, expand=False, fill=False, padding=0)

        self.curve_shape = None

    def hide(self):
        self.form_label.hide()
        self.forms_combo_box.hide()
        self.form_button_box.hide()

    def show(self):
        self.form_label.show()
        self.forms_combo_box.show()
        self.form_button_box.show()

    def add_into_grid(self, grid, start_row):
        r = start_row
        grid.attach(self.form_label, left=0, top=r, width=3, height=1)
        grid.attach(self.forms_combo_box, left=0, top=r+1, width=3, height=1)
        grid.attach(self.form_button_box, left=0, top=r+2, width=3, height=1)
        r += 3
        return r

    def set_curve_shape(self, curve_shape):
        if self.curve_shape == curve_shape: return
        self.curve_shape = curve_shape
        self.apply_form_button.hide()
        self.rename_form_button.hide()
        self.save_form_button.hide()
        self.update()

    def update(self):
        if self.curve_shape:
            values = sorted(self.curve_shape.forms.keys())
        else:
            values = None
        self.forms_combo_box.build_and_set_model(values)

    def forms_combo_box_changed(self, widget):
        form_name = self.forms_combo_box.get_value()
        if form_name:
            self.apply_form_button.show()
            self.rename_form_button.show()
            self.save_form_button.show()
        else:
            self.apply_form_button.hide()
            self.rename_form_button.hide()
            self.save_form_button.hide()

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
                "Rename form", "Rename the form [{0}] to, -".format(form_name))
        if dialog.run() == Gtk.ResponseType.OK:
            new_form_name = dialog.get_input_text().strip()
            if new_form_name and self.curve_shape.rename_form(form_name, new_form_name):
                self.update()
                self.forms_combo_box.set_value(new_form_name)
        dialog.destroy()

    def save_form_button_clicked(self, widget):
        form_name = self.forms_combo_box.get_value()
        if form_name:
            self.curve_shape.save_form(form_name)

    def insert_slice_button_clicked(self, widget):
        form_name = self.forms_combo_box.get_value()
        if form_name:
            prop_data = dict(type="form", start_form=form_name, end_form=None)
            self.insert_time_slice_callback(self.curve_shape, "internal", 0., 1., prop_data)

