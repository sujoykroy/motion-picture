from gi.repository import Gtk
from ..commons import *
from ..gui_utils import NameValueComboBox

class CameraViewerDialog(Gtk.Dialog):
    def __init__(self, parent, title="Viewer", width=400, height = 200):
        Gtk.Dialog.__init__(self, title, parent, 0,())
        self.set_default_size(width, height)
        self.connect("delete-event", self.quit)

        self.master_editor = parent
        box = self.get_content_area()

        self.viewer_box = CamerViewerBox(parent)
        box.pack_start(self.viewer_box, expand=True, fill=True, padding=5)

        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(bottom_box, expand=False, fill=False, padding=5)

        bottom_box.pack_start(Gtk.Label("Camera"), expand=False, fill=False, padding=5)
        self.camera_combo_box = NameValueComboBox()
        self.camera_combo_box.connect("changed", self.camera_combo_changed)
        bottom_box.pack_start(self.camera_combo_box, expand=False, fill=False, padding=5)

        self.rebuild()
        self.show_all()

    def quit(self, widget, event):
        self.master_editor.on_quit_camera_view()

    def camera_combo_changed(self, camera_combo_box):
        self.viewer_box.camera = camera_combo_box.get_value()
        self.viewer_box.redraw()

    def redraw(self):
        self.viewer_box.redraw()

    def rebuild(self):
        camera_list = [["None", None]]
        camera_names = self.master_editor.doc.get_camera_names()
        for name in sorted(camera_names):
            camera_list.append([name, self.master_editor.doc.get_shape_by_name(name)])
        self.camera_combo_box.build_and_set_model(camera_list)

class CamerViewerBox(Gtk.Box):
    def __init__(self, master_editor):
        Gtk.Box.__init__(self)

        self.master_editor = master_editor
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.on_drawing_area_draw)

        self.pack_start(self.drawing_area, expand=True, fill=True, padding=5)

        self.camera = None

    def redraw(self):
        self.drawing_area.queue_draw()

    def on_drawing_area_draw(self, widget, ctx):
        doc = self.master_editor.doc
        if not doc:
            return
        multi_shape = doc.get_main_multi_shape()

        if self.camera:
            view_width = self.camera.width
            view_height = self.camera.height
        else:
            view_width = doc.width
            view_height = doc.height

        dw_width = self.drawing_area.get_allocated_width()
        dw_height = self.drawing_area.get_allocated_height()

        draw_rounded_rectangle(ctx, 0, 0, dw_width, dw_height, 0)
        draw_fill(ctx, "ff0000")

        sx, sy = dw_width/view_width, dw_height/view_height
        scale = min(sx, sy)
        ctx.translate((dw_width-scale*view_width)*.5, (dw_height-scale*view_height)*.5)
        ctx.scale(scale, scale)

        draw_rounded_rectangle(ctx, 0, 0, view_width, view_height, 0)
        draw_fill(ctx, "ffffff")

        if self.camera:
            self.camera.paint_screen(ctx, view_width, view_height, cam_scale=scale)
        else:
            multi_shape.draw(ctx, root_shape=multi_shape)

