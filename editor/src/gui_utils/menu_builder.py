from gi.repository import Gio, GLib, Gtk
import os

def create_attribute_xml(name, value):
    return "<attribute name=\"{0}\">{1}</attribute>".format(name, value)

class TopMenu(object):
    def __init__(self, id):
        self.id = id
        self.items = []

    def get_xml_lines(self):
        lines = []
        lines.append("<menu id=\"{0}\">".format(self.id))
        for item in self.items:
            lines.extend(item.get_xml_lines())
        lines.append("</menu>")
        return lines

    def submenu(self, name):
        submenu = Submenu(name)
        self.items.append(submenu)
        return submenu

    def get_item(self, name):
        for submenu in self.items:
            item = submenu.get_item(name)
            if item: return item
        return None

class Submenu(object):
    def __init__(self, label):
        self.name = label.replace("_", "")
        self.label = label
        self.items = []

    def get_xml_lines(self):
        lines = []
        lines.append("<submenu>")
        lines.append(create_attribute_xml("label", self.label))
        for item in self.items:
            lines.extend(item.get_xml_lines())
        lines.append("</submenu>")
        return lines

    def section(self):
        section = MenuSection()
        self.items.append(section)
        return section

    def submenu(self, name):
        submenu = Submenu(name)
        self.items.append(submenu)
        return submenu

    def item(self, label, action, target=None):
        item = MenuItem(label, action, target)
        self.items.append(item)
        return item

    def get_item(self, name):
        if self.name == name: return self
        for item in self.items:
            ft = item.get_item(name)
            if ft: return ft
        return None

class MenuSection(object):
    def __init__(self):
        self.items = []

    def get_xml_lines(self):
        lines = []
        lines.append("<section>")
        for item in self.items:
            lines.extend(item.get_xml_lines())
        lines.append("</section>")
        return lines

    def submenu(self, name):
        submenu = Submenu(name)
        self.items.append(submenu)
        return submenu

    def item(self, label, action, target=None):
        item = MenuItem(label, action, target)
        self.items.append(item)
        return item

    def get_item(self, name):
        for item in self.items:
            ft = item.get_item(name)
            if ft: return ft
        return None

class MenuItem(object):
    def __init__(self, label, action, target):
        self.name = label.replace("_", "")
        self.label = label
        self.action = action
        self.target = target
        self.accel = None

    def get_item(self, name):
        if self.name == name: return self

    def get_xml_lines(self):
        lines = []
        lines.append("<item>")
        lines.append(create_attribute_xml("label", self.label))
        lines.append(create_attribute_xml("action", self.action))
        if self.target:
            lines.append(create_attribute_xml("target", self.target))
        if self.accel:
            lines.append(create_attribute_xml("accel", self.accel.replace("<", "&lt;").replace(">", "&gt;")))
        lines.append("</item>")
        return lines

    def set_accel(self, accel):
        self.accel = accel

    def get_action_name_only(self):
        return self.action.split(".")[-1]

    def get_target_value(self):
        if isinstance(self.target, str):
            return GLib.Variant.new_string(self.target)

    def is_window_action(self):
        return self.action.split(".")[0] == "win"

class Object(object):
    pass

class MenuBar(object):
    def __init__(self, recent_files):
        self.top_menu = TopMenu("menubar")

        self.actions = Object()
        file_menu = self.top_menu.submenu("File")

        file_edit_section = file_menu.section()
        new_menu = file_edit_section.submenu("New")
        self.action(new_menu, "Icon", "app.create_new_document", "400x400")
        self.action(new_menu, "Document", "app.create_new_document", "400x300")
        self.action(file_edit_section, "Open", "app.open_document", "")

        recent_menu = file_edit_section.submenu("Open Recent")
        for filepath in recent_files:
            name = os.path.basename(filepath)
            self.action(recent_menu, name, "app.open_document", filepath)

        self.action(file_edit_section, "Save", "win.save_document")
        self.action(file_edit_section, "Save As", "win.save_as_document")

        export_menu = file_menu.submenu("Export to")
        self.action(export_menu, "PNG Image", "export_to_png_image")

        edit_menu = self.top_menu.submenu("Edit")
        edit_shape_menu = edit_menu.submenu("Shape")
        self.action(edit_shape_menu, "Insert Break", "win.insert_break_in_shape")
        self.action(edit_shape_menu, "Join Points", "win.join_points_of_shape")
        self.action(edit_shape_menu, "Delete Point", "win.delete_point_of_shape")

        shapes_menu = self.top_menu.submenu("Shapes")

        shape_edit_section = shapes_menu.section()
        self.action(shape_edit_section, "Duplicate", "win.duplicate_shape")
        align_menu = shape_edit_section.submenu("Align")
        self.action(align_menu, "X", "win.align_shapes", "x")
        self.action(align_menu, "Y", "win.align_shapes", "y")
        self.action(align_menu, "XY", "win.align_shapes", "xy")
        self.action(shape_edit_section, "Delete", "win.delete_shape")

        shape_create_section = shapes_menu.section()
        self.action(shape_create_section, "Rectangle", "win.create_new_shape", "rect")
        self.action(shape_create_section, "Oval", "win.create_new_shape", "oval")
        self.action(shape_create_section, "Curve", "win.create_new_shape", "curve")
        self.action(shape_create_section, "Polygon", "win.create_new_shape", "polygon")

        shape_grouping_section = shapes_menu.section()
        self.action(shape_grouping_section, "Join into Group", "win.create_group")
        self.action(shape_grouping_section, "Break Group", "win.break_group")

        help_menu = self.top_menu.submenu("Help")
        self.action(help_menu, "About", "app.about")

    def action(self, section, label, action, target=None):
        fname = action.split(".")[-1]
        setattr(self.actions, fname, fname)
        return section.item(label, action, target)

    def get_builder(self):
        builder = Gtk.Builder()
        lines = []
        lines.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        lines.append("<interface>")
        lines.extend(self.top_menu.get_xml_lines())
        lines.append("</interface>")
        xml_string = "\n".join(lines)
        builder.add_from_string(xml_string)
        return builder

    def get_item(self, path):
        last_item = self.top_menu
        matched = False
        for menu_name in path.split("/"):
            last_item = last_item.get_item(menu_name)
            matched = (last_item is not None)
            if not matched:
                break
        if matched:
            return last_item
        else:
            return None

    def load_accelerators(self, filename):
        f = open(filename, "r")
        for line in f:
            line = line.strip()
            if not line: continue
            its  = line.split(",")
            if len(its)<2: continue
            path = its[0].strip()
            accel = its[1].strip()

            matched_item = self.get_item(path)
            if matched_item:
                matched_item.set_accel(accel)
