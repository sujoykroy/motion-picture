from gi.repository import Gio, GLib, Gtk
import os

def create_attribute_xml(name, value):
    return "<attribute name=\"{0}\">{1}</attribute>".format(name, value)

class Object(object):
    pass

class TopMenu(object):
    def __init__(self, id):
        self.id = id
        self.items = []
        self.actions = Object()
        self.tool_rows = []
        self.menu_items = dict()

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
            if submenu.name == name: return submenu
        return None

    def add(self, path, icon=None, accel=None,
                        action_name=None, action_param=None, action_state=None,
                        icon_scale=1., desc=None):
        last_item = self
        menu_names = path.split("/")
        for i in range(len(menu_names)):
            menu_name = menu_names[i]
            item = last_item.get_item(menu_name)
            if item is None:
                if i == 0:
                    item = last_item.submenu(menu_name)
                elif menu_name[0] == "<" and menu_name[-1] == ">":
                    item = last_item.section(menu_name)
                elif i == len(menu_names)-1 and action_name:
                    item = last_item.item(MenuItem(
                        label=menu_name, accel=accel, icon=icon,
                        action=action_name, target=action_param,
                        state=action_state))
                    item.icon_scale = icon_scale
                    item.desc = desc
                    fname = action_name.split(".")[-1]
                    setattr(self.actions, fname, fname)
                    self.menu_items[path] = item
                else:
                    item = last_item.submenu(menu_name)
            last_item = item
        return last_item

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

    def section(self, name):
        section = MenuSection(name)
        self.items.append(section)
        return section

    def submenu(self, name):
        submenu = Submenu(name)
        self.items.append(submenu)
        return submenu

    def item(self, item):
        self.items.append(item)
        return item

    def get_item(self, name):
        for item in self.items:
            if item.name == name: return item
        return None

class MenuSection(object):
    def __init__(self, name):
        self.items = []
        self.name = name

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

    def item(self, item):
        self.items.append(item)
        return item

    def get_item(self, name):
        for item in self.items:
            if item.name == name: return item
        return None

class MenuItem(object):
    def __init__(self, label, action, target=None, accel=None, icon=None, state=None):
        self.name = label.replace("_", "")
        self.label = label
        self.action = action
        self.target = target
        self.accel = accel
        self.icon = icon
        self.state = state
        if self.target is None:
            self.target = self.state
        self.icon_scale = 1.
        self.desc = None

    def get_xml_lines(self):
        lines = []
        lines.append("<item>")
        lines.append(create_attribute_xml("label", self.label))
        lines.append(create_attribute_xml("action", self.action))
        if self.target is not None:
            lines.append(create_attribute_xml("target", self.target))
        if self.accel:
            lines.append(create_attribute_xml("accel",
                self.accel.replace("<", "&lt;").replace(">", "&gt;")))
        lines.append("</item>")
        return lines

    def get_action_name_only(self):
        return self.action.split(".")[-1]

    def get_target_value(self):
        if isinstance(self.target, str):
            return GLib.Variant.new_string(self.target)

    def is_window_action(self):
        return self.action.split(".")[0] == "win"

    def get_tooltip_text(self):
        text = self.desc if self.desc else self.name
        if self.accel:
            text += " \n" + self.accel
        return text

    def get_action_type(self):
        if type(self.target) is str or type(self.state) is str:
            return GLib.VariantType.new("s")
        elif type(self.target) is bool or type(self.state) is bool:
            return GLib.VariantType.new("b")
        return None

    def get_state(self):
        if type(self.state) is str:
            return GLib.Variant.new_string(self.state)
        elif type(self.state) is bool:
            return GLib.Variant.new_boolean(self.state)
        return None

    def is_boolean_stateful(self):
        if self.state is None: return False
        return type(self.state) is bool

    def is_string_stateful(self):
        if self.state is None: return False
        return type(self.state) is str

class MenuBar(object):
    def __init__(self, top_menu, predrawn_folder):
        self.top_menu = top_menu
        self.actions = self.top_menu.actions
        self.tool_rows = top_menu.tool_rows
        self.menu_items = top_menu.menu_items

      for filename in os.listdir(predrawn_folder):
            name = ".".join(os.path.basename(filename).split(".")[:-1])
            icon = os.path.join(os.path.basename(predrawn_folder), name)
            name = name.upper()[0] + name[1:]
            path = "Shapes/Pre-Drawn/" + name
            menu_item = self.top_menu.add(path=path, icon=icon,
                action_name="win.create_new_shape", action_state=filename)
            menu_item.icon_scale = 2

    def get_builder(self):
        builder = Gtk.Builder()
        lines = []
        lines.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        lines.append("<interface>")
        lines.extend(self.top_menu.get_xml_lines())
        lines.append("</interface>")
        xml_string = "\n".join(lines)
        f = open("/home/sujoy/Temporary/output.xml", "w")
        f.write(xml_string)
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

