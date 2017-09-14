from gi.repository import Gtk
from ..gui_utils import *

class LinkedToHBox(Gtk.HBox):
    def __init__(self, shape_items, delete_callback):
        Gtk.HBox.__init__(self)
        self.shape_combo_box = ImageComboBox()
        self.shape_combo_box.build_and_set_model(shape_items)
        self.pack_start(self.shape_combo_box, expand=False, fill=False, padding=0)
        self.prop_name_entry = Gtk.Entry()
        self.pack_start(self.prop_name_entry, expand=False, fill=False, padding=0)
        self.delete_button = Gtk.Button("Remove")
        self.delete_button.connect("clicked", self.delete_button_clicked)
        self.pack_start(self.delete_button, expand=False, fill=False, padding=0)
        self.delete_callback = delete_callback
        self.show_all()

    def delete_button_clicked(self, widget):
        self.delete_callback(self)

    def set_shape(self, shape):
        self.shape_combo_box.set_value(shape.get_name())

    def set_prop_name(self, prop_name):
        self.prop_name_entry.set_text(prop_name)

    def get_shape_name(self):
        return self.shape_combo_box.get_value()

    def get_prop_name(self):
        return self.prop_name_entry.get_text().strip()

class CustomPropEditor(Gtk.Dialog):
    def __init__(self, parent, shape, width=400, height = 600):
        Gtk.Dialog.__init__(self, "Custom Prop Editor", parent, 0, tuple())
        self.set_default_size(width, height)

        self.shape = shape
        self.parent = parent
        box = self.get_content_area()

        shape_hbox = Gtk.HBox()
        box.pack_start(shape_hbox, expand=False, fill=False, padding=0)

        shape_image = Gtk.Image.new_from_pixbuf(shape.get_pixbuf(64))
        shape_hbox.pack_start(shape_image, expand=False, fill=False, padding=0)

        shape_name_label = Gtk.Label()
        shape_name_label.set_text(shape.get_name())
        shape_hbox.pack_start(shape_name_label, expand=False, fill=False, padding=0)

        prop_hbox = Gtk.HBox()
        box.pack_start(prop_hbox, expand=False, fill=False, padding=0)

        self.prop_name_entry = Gtk.Entry()
        prop_hbox.pack_start(self.prop_name_entry, expand=True, fill=True, padding=0)

        self.prop_type_combo_box = NameValueComboBox()
        self.prop_type_combo_box.build_and_set_model(["number", "color", "font", "point", "text"])
        prop_hbox.pack_start(self.prop_type_combo_box, expand=False, fill=False, padding=0)

        self.linked_to_vbox = Gtk.VBox()
        self.linked_to_vbox_container = Gtk.ScrolledWindow()
        self.linked_to_vbox_container.set_size_request(-1, 400)
        self.linked_to_vbox_container.add_with_viewport(self.linked_to_vbox)
        box.pack_start(self.linked_to_vbox_container, expand=False, fill=False, padding=10)

        button_hbox = Gtk.HBox()
        box.pack_end(button_hbox, expand=False, fill=False, padding=10)

        self.add_linked_to_button = Gtk.Button("Add Linked To")
        self.add_linked_to_button.connect("clicked", self.add_linked_to_button_clicked)
        self.save_button = Gtk.Button("Save")
        self.save_button.connect("clicked", self.save_button_clicked)
        self.delete_button = Gtk.Button("Delete")
        self.delete_button.connect("clicked", self.delete_button_clicked)
        self.cancel_button = Gtk.Button("Cancel")
        self.cancel_button.connect("clicked", self.cancel_button_clicked)

        button_hbox.pack_end(self.save_button, expand=False, fill=False, padding=0)
        button_hbox.pack_end(self.cancel_button, expand=False, fill=False, padding=0)
        button_hbox.pack_end(self.add_linked_to_button, expand=False, fill=False, padding=0)
        button_hbox.pack_start(self.delete_button, expand=False, fill=False, padding=0)


        self.shape_items = []
        for child_shape in shape.shapes:
            self.shape_items.append([child_shape.get_pixbuf(32), child_shape.get_name()])

        self.set_custom_prop(None)
        self.show_all()

    def add_linked_to_button_clicked(self, widget):
        self.get_new_linked_to_hbox()

    def get_new_linked_to_hbox(self):
        linked_to_hbox = LinkedToHBox(self.shape_items, self.on_linked_to_deleted)
        self.linked_to_vbox.pack_start(linked_to_hbox, expand=False, fill=False, padding=5)
        return linked_to_hbox

    def on_linked_to_deleted(self, linked_to_hbox):
        self.linked_to_vbox.remove(linked_to_hbox)

    def save_button_clicked(self, widget):
        if self.custom_prop is None:
            custom_prop_name  = self.prop_name_entry.get_text().strip()
            if not custom_prop_name:
                return
            custom_prop_type = self.prop_type_combo_box.get_value()
            if not self.shape.add_custom_prop(custom_prop_name, custom_prop_type):
                notice = NoticeDialog(self.parent, text="Prop name is not valid")
                return
            self.custom_prop = self.shape.custom_props.get_prop(custom_prop_name)
            cross_check = False
            proxy_custom_prop = self.custom_prop
        else:
            proxy_custom_prop = self.custom_prop.copy(self.shape)
            del proxy_custom_prop.linked_to_items[:]
            cross_check = True

        for linked_to_hbox in self.linked_to_vbox.get_children():
            linked_to_shape_name = linked_to_hbox.get_shape_name()
            if not linked_to_shape_name:
                continue
            linked_to_prop_name = linked_to_hbox.get_prop_name()
            if not linked_to_prop_name:
                continue
            if not self.shape.shapes.key_exists(linked_to_shape_name):
                continue
            self.custom_prop.add_linked_to(
                self.shape.shapes[linked_to_shape_name],
                linked_to_prop_name)
            proxy_custom_prop.add_linked_to(
                self.shape.shapes[linked_to_shape_name],
                linked_to_prop_name)

        if cross_check:
            remove_items = []
            for linked_to in self.custom_prop.linked_to_items:
                if proxy_custom_prop.get_linked_to(linked_to.shape, linked_to.prop_name):
                    continue
                remove_items.append(linked_to)
            for linked_to in remove_items:
                self.custom_prop.remove_linked_to(linked_to.shape, linked_to.prop_name)

        self.close()

    def delete_button_clicked(self, widget):
        dialog = YesNoDialog(
            self.parent, "Deletr Custom Prop",
            "Are you sure about deleting this custom-prop?")
        if dialog.run() == Gtk.ResponseType.NO:
            dialog.destroy()
            return
        dialog.destroy()
        self.shape.custom_props.remove_prop(self.custom_prop.prop_name)
        self.close()

    def cancel_button_clicked(self, widget):
        self.close()

    def close(self):
        self.response(Gtk.ResponseType.NONE)

    def set_custom_prop(self, custom_prop):
        self.custom_prop = custom_prop
        if self.custom_prop:
            self.prop_name_entry.set_text(self.custom_prop.prop_name)
            self.prop_name_entry.set_editable(False)
            self.prop_type_combo_box.set_value(self.custom_prop.get_prop_type_name())
            self.prop_type_combo_box.set_sensitive(False)

            for linked_to in self.custom_prop.linked_to_items:
                linked_to_hbox = self.get_new_linked_to_hbox()
                linked_to_hbox.set_shape(linked_to.shape)
                linked_to_hbox.set_prop_name(linked_to.prop_name)
        else:
            self.prop_name_entry.set_text("")
            self.prop_name_entry.set_editable(True)
            self.prop_type_combo_box.set_value("number")
            self.prop_type_combo_box.set_sensitive(True)

