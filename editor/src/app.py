from gi.repository import Gtk, GLib, Gio
from gi.repository import Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
import sys, os, cairo

from editors import MasterEditor
from gui_utils import *
from gui_utils.menu_builder import MenuItem
from document import Document
import settings as Settings
from settings import EditingChoice
from commons.draw_utils import draw_text
from tasks import *
from shapes import MultiShape, CurveShape
from shape_creators import CurveShapeCreator

THIS_FOLDER = os.path.dirname(__file__)

def new_action(parent, menu_item):
    action_name = menu_item.get_action_name_only()
    if parent.lookup_action(action_name): return
    if hasattr(parent, action_name):
        parameter_type = menu_item.get_action_type()
        state = menu_item.get_state()
        if state is None:
            action = Gio.SimpleAction.new(action_name, parameter_type=parameter_type)
            action.connect("activate", getattr(parent, action_name))
        else:
            action = Gio.SimpleAction.new_stateful(action_name,
                                    parameter_type=parameter_type, state=state)
            action.connect("change_state", getattr(parent, action_name))
            action.tool_buttons = []
            action.menu_item = menu_item
        parent.add_action(action)

def change_action_tool_buttons(action):
    if not hasattr(action, "tool_buttons"): return
    for tool_button in action.tool_buttons:
        if not isinstance(tool_button, Gtk.ToggleToolButton): continue
        action_state = action.get_state()
        menu_item = action.menu_item
        if menu_item.is_boolean_stateful():
            is_active = action_state.get_boolean()
        elif menu_item.is_string_stateful():
            is_active = (tool_button.action_state_value == action_state.get_string())
        tool_button.props.active = is_active

class ApplicationWindow(MasterEditor):
    def __init__(self, parent):
        MasterEditor.__init__(self)
        self.parent = parent

    def build_toolbar(self, menubar):
        for tool_row in menubar.tool_rows:
            toolbar = Gtk.Toolbar()
            self.toolbar_container.pack_start(toolbar, expand=False, fill=False, padding=0)

            for tool_segment in tool_row:
                toolbar.insert(Gtk.SeparatorToolItem(), -1)
                if type(tool_segment) is str:
                    tool_segment = menubar.get_item(tool_segment)
                    tool_segment = tool_segment.items
                for menu_item in tool_segment:
                    if menu_item is str:
                        menu_item = menubar.get_item(tool_item)
                    if not isinstance(menu_item, MenuItem): continue
                    if menu_item.icon:
                        filename = os.path.join(Settings.ICONS_FOLDER, menu_item.icon + ".xml")
                        doc = Document(filename=filename)
                        pixbuf = doc.get_pixbuf(width=20, height=20)
                        tool_widget = Gtk.Image.new_from_pixbuf(pixbuf)
                    else:
                        tool_widget = Gtk.Label(menu_item.name)

                    add_tool_button_into_actions = False
                    if menu_item.get_state() is not None:
                        tool_button = Gtk.ToggleToolButton.new()
                        tool_button.set_icon_widget(tool_widget)
                        tool_button.set_label(menu_item.label)
                        tool_button.action_state_value = menu_item.state
                        tool_button.action_variant_state_value = menu_item.get_state()
                        if menu_item.is_window_action():
                            obj = self
                        else:
                            obj = self.parent
                        action = obj.lookup_action(menu_item.get_action_name_only())
                        if action and hasattr(action, "tool_buttons"):
                            action.tool_buttons.append(tool_button)
                        if menu_item.is_boolean_stateful():
                            action_state_value = menu_item.get_state()
                        elif menu_item.is_string_stateful():
                            action_state_value = False
                        tool_button.props.active = action_state_value
                    else:
                        tool_button = Gtk.ToolButton.new(tool_widget, menu_item.label)
                    tool_button.set_tooltip_text(menu_item.get_tooltip_text())

                    tool_button.connect("clicked", self.tool_button_clicked, menu_item)
                    toolbar.insert(tool_button, -1)
        self.toolbar_container.show_all()

    def tool_button_clicked(self, widget, menu_item):
        if menu_item.is_window_action():
            obj = self
        else:
            obj = self.parent
        action = obj.lookup_action(menu_item.get_action_name_only())
        if action:
            if menu_item.state is None:
                action.activate(menu_item.get_target_value())
            else:
                if menu_item.is_boolean_stateful():
                    action.change_state(GLib.Variant.new_boolean(widget.get_active()))
                elif widget.get_active():
                    action.change_state(widget.action_variant_state_value)

    def save_document(self, action, parameter):
        if not self.doc.filename:
            filename = FileOp.choose_file(self, purpose="save")
            if filename:
                self.doc.save(filename)
                self.show_filename()
                self.parent.recent_manager.add_item(filename)
        else:
            self.doc.save()

    def save_as_document(self, action, parameter):
        filename = FileOp.choose_file(self, purpose="save_as")
        if filename:
            self.doc.save(filename)
            self.show_filename()
            self.parent.recent_manager.add_item(filename)

    def create_new_shape(self, action, parameter):
        action.set_state(parameter)
        change_action_tool_buttons(action)
        shape_type = parameter.get_string()
        if shape_type == "image":
            filename = FileOp.choose_file(self, purpose="open", file_types=[["Image", "image/*"]])
            if not filename:
                return
            if self.shape_manager.create_image_shape(filename):
                self.redraw()
        else:
            self.set_shape_creation_mode(shape_type)
        #action.set_state(GLib.Variant.new_string(""))
        #change_action_tool_buttons(action)

    def insert_break_in_shape(self, action, parameter):
        if self.shape_manager.insert_break():
            self.redraw()

    def join_points_of_shape(self, action, parameter):
        if self.shape_manager.join_points():
            self.redraw()

    def delete_point_of_shape(self, action, parameter):
        if self.shape_manager.delete_point():
            self.redraw()

    def extend_point_of_shape(self, action, parameter):
        if self.shape_manager.extend_point():
            self.redraw()

    def duplicate_shape(self, action, parameter):
        if self.shape_manager.duplicate_shape():
            self.redraw()

    def delete_shape(self, action, parameter):
        self.shape_manager.delete_selected_shape()
        self.time_line_editor.update()
        self.redraw()

    def create_shape_group(self, action, parameter):
        self.shape_manager.combine_shapes()
        self.redraw()

    def align_shapes(self, action, parameter):
        direction = parameter.get_string()
        if direction == "x":
            x_dir = True
            y_dir = False
        elif direction == "y":
            x_dir = False
            y_dir = True
        elif direction == "xy":
            x_dir = True
            y_dir = True
        self.shape_manager.align_shapes(x_dir=x_dir, y_dir=y_dir)
        self.redraw()

    def convert_shape_to(self, action, parameter):
        if self.shape_manager.convert_shape_to(parameter.get_string()):
            self.redraw()

    def undo_redo(self, action, parameter):
        urnam = parameter.get_string()
        if urnam == "undo":
            task = self.doc.reundo.get_undo_task()
        else:
            task = self.doc.reundo.get_redo_task()
        if not task: return
        self.shape_manager.delete_shape_editor()
        if isinstance(task, ShapeStateTask):
            getattr(task, urnam)(self.doc)
            if isinstance(task, ShapeDeleteTask) or isinstance(task, ShapeAddTask):
                self.shape_manager.reload_shapes()
            elif self.shape_manager.shape_creator:
                shape = self.shape_manager.shape_creator.shape
                if isinstance(shape, CurveShape):
                    self.shape_manager.shape_creator = CurveShapeCreator(
                            shape, -1, -1)
                else:
                    self.shape_manager.shape_creator = None
            self.redraw()

    def lock_shape_movement(self, action, parameter):
        action.set_state(parameter)
        EditingChoice.LOCK_MOVEMENT = parameter.get_boolean()
        change_action_tool_buttons(action)

class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self,
                application_id="bk2suz.motion_picture",
                flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

        self.open_filename = None

        self.connect("activate", self.on_activate)
        self.connect("command-line", self.on_command_line)

    def on_command_line(self, app, command_line):
        self.argv = command_line.get_arguments()
        if len(self.argv) > 1:
            self.open_filename = self.argv[1]
        self.activate()
        return 0

    def create_new_document(self, action, parameter):
        w, h = parameter.get_string().split("x")
        win = self.new_app_window()
        win.open_document(width=float(w), height=float(h))
        win.redraw()

    def open_document(self, action, parameter):
        win = None
        newly_created = True
        for w in self.get_windows():
            if w.doc.filename is None:
                win = w
                newly_created = False
                break
        if win is None:
            win = self.new_app_window()

        if parameter:
            filename = parameter.get_string()
        else:
            filename = FileOp.choose_file(win, purpose="open")
        if filename:
            self.recent_manager.add_item(filename)
            win.open_document(filename)
        elif newly_created:
            self.remove_window(win)
            win.destroy()

    def new_app_window(self):
        win = ApplicationWindow(self)

        for menu_item in self.menubar.menu_items.values():
            if not menu_item.is_window_action(): continue
            new_action(win, menu_item)

        win.build_toolbar(self.menubar)
        self.add_window(win)
        win.show_all()
        win.init_interface()
        return win

    def on_activate(self, app):
        self.recent_manager = Gtk.RecentManager.get_default()
        self.app_name = os.path.basename(self.argv[0])
        recent_files = []
        for recent_info in self.recent_manager.get_items():
            if not recent_info.has_application(self.app_name): continue
            if recent_info.get_mime_type() != "application/xml": continue
            filepath = recent_info.get_uri()
            recent_files.append(filepath)
        self.menubar = MenuBar(recent_files, Settings.menus.TopMenuItem)

        for menu_item in self.menubar.menu_items.values():
            if menu_item.is_window_action(): continue
            new_action(self, menu_item)

        builder = self.menubar.get_builder()
        self.set_menubar(builder.get_object("menubar"))

        win = self.new_app_window()
        if self.open_filename:
            win.open_document(self.open_filename)

