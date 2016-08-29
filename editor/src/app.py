from gi.repository import Gtk, GLib, Gio
from gi.repository import Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
import sys, os, cairo

from editors import MasterEditor
from gui_utils import *
from document import Document
import settings as Settings
from commons.draw_utils import draw_text

THIS_FOLDER = os.path.dirname(__file__)

def new_action(parent, action_name, param_type=None):
    if hasattr(parent, action_name):
        action = Gio.SimpleAction.new(action_name, parameter_type=param_type)
        action.connect("activate", getattr(parent, action_name))
        parent.add_action(action)

def text_icon_pixbuf(text):
    padding = 0
    width = 30
    height = 20+2*padding
    pixbuf = Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, width, height)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(), pixbuf.get_height())
    ctx = cairo.Context(surface)
    Gdk.cairo_set_source_pixbuf(ctx, pixbuf, 0, 0)

    draw_text(ctx, text, x=0, y=0, width=width, height=height, fit_width=True,
              back_color="d5d568", padding=padding)

    surface= ctx.get_target()
    pixbuf= Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())

    return pixbuf

class ApplicationWindow(MasterEditor):
    def __init__(self, parent, menubar):
        MasterEditor.__init__(self)
        self.parent = parent

        f = open(Settings.MENU_ACCEL_ICON_FILE, "r")

        for line in f:
            its = line.split(",")
            if len(its)<3: continue

            path = its[0].strip()
            icon = its[2].strip()

            menu_item = menubar.get_item(path)
            label_name = its[3].strip() if len(its)>3 else menu_item.name

            filename = os.path.join(Settings.ICONS_FOLDER, icon + ".xml")
            doc = Document(filename=filename)
            pixbuf = doc.get_pixbuf(width=20, height=20)
            #tool_button = Gtk.ToolButton.new(Gtk.Image.new_from_pixbuf(pixbuf), menu_item.name)
            tool_button = Gtk.ToolButton.new(Gtk.Label(label_name), menu_item.name)
            #tool_button = Gtk.ToolButton.new(Gtk.Image.new_from_pixbuf(text_icon_pixbuf(label_name)), menu_item.name)
            tool_button.connect("clicked", self.tool_button_clicked, menu_item)
            self.toolbar.insert(tool_button, -1)
        self.toolbar.show()

    def tool_button_clicked(self, widget, menu_item):
        if menu_item.is_window_action():
            obj = self
        else:
            obj = self.parent
        action = obj.lookup_action(menu_item.get_action_name_only())
        if action:
            action.activate(menu_item.get_target_value())

    def save_document(self, action, parameter):
        if not self.doc.filename:
            filename = FileOp.choose_file(self, purpose="save")
            if filename:
                self.doc.save(filename)
                self.show_filename()
        else:
            self.doc.save()

    def save_as_document(self, action, parameter):
        filename = FileOp.choose_file(self, purpose="save_as")
        if filename:
            self.doc.save(filename)
            self.show_filename()

    def create_new_shape(self, action, parameter):
        self.set_shape_creation_mode(parameter.get_string())

    def insert_break_in_shape(self, action, parameter):
        if self.shape_manager.insert_break():
            self.redraw()

    def join_points_of_shape(self, action, parameter):
        if self.shape_manager.join_points():
            self.redraw()

    def duplicate_shape(self, action, parameter):
        if self.shape_manager.duplicate_shape():
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

class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self,
                application_id="bk2suz.motion_picture",
                flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

        self.open_filename = None

        self.connect("startup", self.on_startup)
        self.connect("activate", self.on_activate)
        self.connect("command-line", self.on_command_line)

    def on_command_line(self, app, command_line):
        argv = command_line.get_arguments()
        if len(argv) > 1:
            self.open_filename = argv[1]
        self.activate()
        return 0

    def on_startup(self, app):
        app_name = os.path.basename(__file__)
        self.recent_manager = Gtk.RecentManager.get_default()
        recent_files = []
        for recent_info in self.recent_manager.get_items():
            if not recent_info.has_application(app_name): continue
            filepath = recent_info.get_uri()
            recent_files.append(filepath)

        self.menubar = MenuBar(recent_files)
        self.menubar.load_accelerators(Settings.MENU_ACCEL_ICON_FILE)

        new_action(self, self.menubar.actions.create_new_document)
        new_action(self, self.menubar.actions.open_document)

        builder = self.menubar.get_builder()
        self.set_menubar(builder.get_object("menubar"))

    def create_new_document(self, action, parameter):
        self.new_app_window()

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
        win = ApplicationWindow(self, self.menubar)

        new_action(win, self.menubar.actions.save_document)
        new_action(win, self.menubar.actions.save_as_document)
        new_action(win, self.menubar.actions.create_new_shape, GLib.VariantType.new("s"))
        new_action(win, self.menubar.actions.insert_break_in_shape)
        new_action(win, self.menubar.actions.join_points_of_shape)
        new_action(win, self.menubar.actions.duplicate_shape)
        new_action(win, self.menubar.actions.align_shapes, GLib.VariantType.new("s"))

        self.add_window(win)
        win.show_all()
        win.init_interface()
        return win

    def on_activate(self, app):
        win = self.new_app_window()
        if self.open_filename:
            win.open_document(self.open_filename)

