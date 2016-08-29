from gi.repository import Gtk, Gdk
import os, math, cairo

from ..shapes import *
from ..gui_utils import *
from ..time_lines import *

from ..document import Document
from shape_manager import ShapeManager
from time_line_editor import TimeLineEditor

from .. import settings as Settings

MODE_NEW_SHAPE_CREATE = "MODE_NEW_SHAPE_CREATE"
SHIFT_KEY_CODE = 65505
SHIFT_CTRL_CODE = 65507

class MasterEditor(Gtk.ApplicationWindow):
    def __init__(self, width=800, height=300, title="MotionPicture"):
        Gtk.ApplicationWindow.__init__(self, title=title, resizable=True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(width, height)
        self.connect("key-press-event", self.on_drawing_area_key_press)
        self.connect("key-release-event", self.on_drawing_area_key_release)

        style_provider = Gtk.CssProvider()
        style_provider.load_from_path(Settings.MAIN_CSS_FILE)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.set_events(Gdk.EventMask.POINTER_MOTION_MASK)

        self.mouse_point = Point(0,0)
        self.mouse_init_point = Point(0,0)

        self.state_mode = None
        self.next_new_shape_type = None

        self.keyboard_object = Keyboard()
        self.doc = None
        self.shape_manager = None
        self.playing = False
        self.drawing_area_mouse_pressed = False
        self.multi_shape_stack = []

        self.root_box = Gtk.VBox()
        self.add(self.root_box)

        self.tool_box = Gtk.HBox()
        self.root_box.pack_start(self.tool_box, expand=False, fill=False, padding=0)
        self.add_new_shape_button("rect", self.tool_box)
        self.add_new_shape_button("oval", self.tool_box)
        self.add_new_shape_button("curve", self.tool_box)
        self.add_new_action_button("group", self.combine_shapes, self.tool_box)
        self.add_new_action_button("delete shape", self.delete_shape, self.tool_box)
        self.toolbar = Gtk.Toolbar()
        self.root_box.pack_start(self.toolbar, expand=False, fill=False, padding=0)

        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.root_box.pack_start(sep, expand=False, fill=False, padding=0)

        self.top_info_bar = Gtk.HBox()
        self.root_box.pack_start(self.top_info_bar, expand=False, fill=False, padding=2)

        editing_label = Gtk.Label()
        editing_label.set_markup(Text.markup(color=Settings.TOP_INFO_BAR_TEXT_COLOR, weight="bold",text="Editing :"))
        self.top_info_bar.pack_start(editing_label, expand=False, fill=False, padding=5)
        self.multi_shape_name_label = Gtk.Label()
        self.top_info_bar.pack_start(self.multi_shape_name_label, expand=False, fill=False, padding=5)

        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.root_box.pack_start(sep, expand=False, fill=False, padding=2)

        self.paned_box_1 = Gtk.VPaned()
        self.root_box.pack_end(self.paned_box_1, expand=True, fill=True, padding = 5)

        self.paned_box_2 = Gtk.HPaned()
        self.paned_box_1.pack1(self.paned_box_2, resize=True, shrink=True)

        self.paned_box_3 = Gtk.HPaned()
        self.paned_box_2.pack2(self.paned_box_3, resize=True, shrink=True)

        self.time_line_editor = TimeLineEditor(self.update_shape_manager,
                                self.show_time_slice_props, self.keyboard_object)
        self.paned_box_1.pack2(self.time_line_editor, resize=True, shrink=True)

        self.left_prop_box = Gtk.VBox()
        left_prop_box_container = Gtk.ScrolledWindow()
        left_prop_box_container.add_with_viewport(self.left_prop_box)

        self.common_shape_prop_box = CommonShapePropBox(self.redraw, self, self.insert_time_slice)
        self.rectangle_shape_prop_box = RectangleShapePropBox(self.redraw, self.insert_time_slice)
        self.oval_shape_prop_box = OvalShapePropBox(self.redraw, self.insert_time_slice)
        self.multi_shape_prop_box = MultiShapePropBox(self.redraw, self.insert_time_slice)

        self.left_prop_box.pack_start(self.common_shape_prop_box, expand=False, fill=False, padding=0)
        self.left_prop_box.pack_start(self.rectangle_shape_prop_box, expand=False, fill=False, padding=0)
        self.left_prop_box.pack_start(self.oval_shape_prop_box, expand=False, fill=False, padding=0)
        self.left_prop_box.pack_start(self.multi_shape_prop_box, expand=False, fill=False, padding=0)

        self.paned_box_2.pack1(left_prop_box_container, resize=True, shrink=True)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_events(
            Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK|\
            Gdk.EventMask.BUTTON_RELEASE_MASK|Gdk.EventMask.SCROLL_MASK)
        self.drawing_area.connect("draw", self.on_drawing_area_draw)
        self.drawing_area.connect("configure-event", self.on_configure_event)
        self.drawing_area.connect("button-press-event", self.on_drawing_area_mouse_press)
        self.drawing_area.connect("button-release-event", self.on_drawing_area_mouse_release)
        self.drawing_area.connect("motion-notify-event", self.on_drawing_area_mouse_move)
        self.drawing_area.connect("scroll-event", self.on_drawing_area_mouse_scroll)

        self.drawing_area_vadjust = Gtk.Adjustment(0, 0, 1., .1, 0, 0)
        self.drawing_area_vscrollbar = Gtk.VScrollbar(self.drawing_area_vadjust)
        self.drawing_area_vscrollbar.connect("value-changed", self.on_drawing_area_scroll, "vert")

        self.drawing_area_hadjust = Gtk.Adjustment(0, 0, 1., .1, 0, 0)
        self.drawing_area_hscrollbar = Gtk.HScrollbar(self.drawing_area_hadjust)
        self.drawing_area_hscrollbar.connect("value-changed", self.on_drawing_area_scroll, "horiz")

        drawing_area_container = Gtk.VBox()

        drawing_area_container_tbox = Gtk.HBox()
        drawing_area_container.pack_start(drawing_area_container_tbox, expand=True,  fill=True, padding=0)
        drawing_area_container.pack_start(self.drawing_area_hscrollbar, expand=False,  fill=True, padding=0)

        drawing_area_container_tbox.pack_start(self.drawing_area, expand=True,  fill=True, padding=0)
        drawing_area_container_tbox.pack_start(self.drawing_area_vscrollbar, expand=False,  fill=True, padding=0)

        self.paned_box_3.pack1(drawing_area_container, resize=True, shrink=True)

        self.right_prop_box = Gtk.VBox()
        right_prop_box_container = Gtk.ScrolledWindow()
        right_prop_box_container.add_with_viewport(self.right_prop_box)
        self.paned_box_3.pack2(right_prop_box_container, resize=True, shrink=True)

        self.multi_shape_internal_prop_box = MultiShapeInternalPropBox(
                            self.redraw, self.load_multi_shape_time_line)
        self.right_prop_box.pack_start(self.multi_shape_internal_prop_box, expand=False, fill=False, padding=0)
        self.multi_shape_internal_prop_box.parent_window = self

        self.time_slice_prop_box = TimeSlicePropBox(self.time_line_editor.update)
        self.right_prop_box.pack_start(self.time_slice_prop_box, expand=False, fill=False, padding=0)

        self.curve_shape_prop_box = CurveShapePropBox(self.redraw, self.insert_time_slice)
        self.curve_shape_prop_box.parent_window = self
        self.right_prop_box.pack_start(self.curve_shape_prop_box, expand=False, fill=False, padding=0)

        #self.show_all()
        #self.maximize()

    def init_interface(self):
        self.show_prop_of(None)
        self.show_time_slice_props(None)

        self.paned_box_2.set_position(180)
        self.paned_box_3.set_position(80)
        self.paned_box_1.set_position(180)

        self.open_document(None)
        ##self.timer_id = GObject.timeout_add(100, self.redraw)

    def show_filename(self):
        filename = self.doc.filename
        if not filename:
            filename = "Untitled"
        else:
            filename = os.path.basename(filename)
        self.set_title("MotionPicture-{0}".format(filename))

    def get_multi_stack_breadcrumb_name(self):
        names = []
        for multi_shape in self.multi_shape_stack:
            names.append(multi_shape.get_name())
        return "->".join(names)

    def add_new_action_button(self, name, click_callback, parent_box):
        button = Gtk.Button(name)
        parent_box.pack_start(button, expand = False, fill= False, padding = 5)
        button.connect("clicked", click_callback)

    def add_new_shape_button(self, shape_type, parent_box):
        button = Gtk.Button("New " + shape_type)
        parent_box.pack_start(button, expand = False, fill= False, padding = 5)
        button.connect("clicked", self.on_new_shape_button_clicked, shape_type)

    def get_drawing_area_size(self):
        w = self.drawing_area.get_allocated_width()
        h = self.drawing_area.get_allocated_height()
        return w, h

    def get_doc_and_multi_shape_point(self, point):
        doc_point = self.shape_manager.document_area_box.transform_point(point)
        shape_point = doc_point.copy()
        for multi_shape in self.multi_shape_stack:
            shape_point = multi_shape.transform_point(shape_point)
        return doc_point, shape_point

    def load_multi_shape(self, multi_shape):
        self.multi_shape_stack.append(multi_shape)
        self.shape_manager = ShapeManager(multi_shape, self.doc)
        w, h = self.get_drawing_area_size()
        self.shape_manager.document_area_box.move_to(w*.5, h*.5)
        self.shape_manager.resize_scollable_area(w, h)

        self.show_prop_of(None)
        self.load_multi_shape_time_line(None)
        self.multi_shape_name_label.set_markup(
            Text.markup(color=Settings.TOP_INFO_BAR_TEXT_COLOR, weight="bold",
                text=self.get_multi_stack_breadcrumb_name()
            )
        )
        self.multi_shape_internal_prop_box.set_multi_shape(multi_shape)
        if multi_shape.timelines:
            timeline_name = sorted(multi_shape.timelines.keys())[0]
            self.load_multi_shape_time_line(multi_shape.timelines[timeline_name])
        self.redraw()

    def load_multi_shape_time_line(self, multi_shape_time_line):
        self.time_line_editor.set_multi_shape_time_line(multi_shape_time_line)

    def open_document(self, filename):
        self.doc = Document(filename)
        del self.multi_shape_stack[:]
        self.load_multi_shape(self.doc.get_main_multi_shape())
        self.show_filename()

    def set_shape_creation_mode(self, shape_type):
        self.next_new_shape_type = shape_type
        self.state_mode = MODE_NEW_SHAPE_CREATE

    def insert_time_slice(self, shape, prop_name, start_value, end_value=None, prop_data=None):
        if not self.time_line_editor.time_line: return
        duration = 5.
        t = self.time_line_editor.get_play_head_time()
        time_line = self.time_line_editor.time_line
        time_slices = []
        if prop_name == "stage_xy":
            time_slice = TimeSlice(start_value.x, start_value.x, duration)
            time_line.insert_shape_prop_time_slice_at(t, shape, "stage_x", time_slice)
            time_slice = TimeSlice(start_value.y, start_value.y, duration)
            time_line.insert_shape_prop_time_slice_at(t, shape, "stage_y", time_slice)
        else:
            if end_value is None:
                end_value = start_value
            time_slice = TimeSlice(start_value, end_value, duration, prop_data=prop_data)
            time_line.insert_shape_prop_time_slice_at(t, shape, prop_name, time_slice)
        self.time_line_editor.update()

    def show_time_slice_props(self, time_slice_box):
        self.time_slice_prop_box.set_time_slice_box(time_slice_box)

    def combine_shapes(self, widget):
        self.shape_manager.combine_shapes()
        self.redraw()

    def delete_shape(self, widget):
        self.shape_manager.delete_selected_shape()
        self.time_line_editor.update()
        self.redraw()

    def set_shape_name(self, shape, name):
        return self.shape_manager.rename_shape(shape, name)

    def show_prop_of(self, shape):
        self.common_shape_prop_box.hide()
        self.rectangle_shape_prop_box.hide()
        self.oval_shape_prop_box.hide()
        self.multi_shape_prop_box.hide()
        self.curve_shape_prop_box.hide()

        if shape != None:
            self.common_shape_prop_box.show()
            self.common_shape_prop_box.set_prop_object(shape)
            if isinstance(shape, RectangleShape):
                self.rectangle_shape_prop_box.show()
                self.rectangle_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, OvalShape):
                self.oval_shape_prop_box.show()
                self.oval_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, MultiShape):
                self.multi_shape_prop_box.show()
                self.multi_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, CurveShape):
                self.curve_shape_prop_box.show()
                self.curve_shape_prop_box.set_curve_shape(shape)

    def update_drawing_area_scrollbars(self):
        w, h = self.get_drawing_area_size()
        self.shape_manager.resize_scollable_area(w, h)
        x_pos, y_pos = self.shape_manager.get_scroll_position(w, h)
        self.drawing_area_vadjust.set_value(y_pos)
        self.drawing_area_hadjust.set_value(x_pos)

    def update_shape_manager(self):
        self.shape_manager.update()
        self.redraw()

    def redraw(self):
        self.drawing_area.queue_draw()
        return self.playing

    def on_new_shape_button_clicked(self, widget, shape_type):
        self.next_new_shape_type = shape_type
        self.state_mode = MODE_NEW_SHAPE_CREATE

    def on_drawing_area_key_press(self, widget, event):
        if event.keyval == SHIFT_KEY_CODE:
            self.keyboard_object.shift_key_pressed = True
        elif event.keyval == SHIFT_CTRL_CODE:
            self.keyboard_object.control_key_pressed = True

    def on_drawing_area_key_release(self, widget, event):
        if event.keyval == SHIFT_KEY_CODE:
            self.keyboard_object.shift_key_pressed = False
        elif event.keyval == SHIFT_CTRL_CODE:
            self.keyboard_object.control_key_pressed = False

    def on_drawing_area_mouse_press(self, widget, event):
        self.mouse_init_point.x = self.mouse_point.x
        self.mouse_init_point.y = self.mouse_point.y
        self.drawing_area_mouse_pressed = True

        if event.button == 1:#Left mouse
            if event.type == Gdk.EventType._2BUTTON_PRESS:#double button click
                if self.shape_manager.has_shape_creator():
                    self.shape_manager.complete_shape_creation()
                elif self.shape_manager.has_designable_multi_shape_selected():
                    multi_shape = self.shape_manager.get_selected_shape()
                    self.load_multi_shape(multi_shape)
                elif self.shape_manager.has_curve_shape_selected():
                    doc_point, shape_point = self.get_doc_and_multi_shape_point(self.mouse_point)
                    self.shape_manager.insert_point_in_curve_at(shape_point)
                elif self.shape_manager.has_no_shape_selected():
                    if len(self.multi_shape_stack)>1:
                        del self.multi_shape_stack[-1]
                        multi_shape = self.multi_shape_stack[-1]
                        del self.multi_shape_stack[-1]
                        self.load_multi_shape(multi_shape)
                return

            doc_point, shape_point = self.get_doc_and_multi_shape_point(self.mouse_point)
            self.shape_manager.select_item_at(doc_point, shape_point,
                                    multi_select=self.keyboard_object.shift_key_pressed)

            if self.shape_manager.get_selected_shape() is None:
                if self.state_mode == MODE_NEW_SHAPE_CREATE and self.shape_manager.shape_creator is None:
                    self.shape_manager.start_creating_new_shape(
                                    self.next_new_shape_type, doc_point, shape_point)
                    self.state_mode = None
            elif self.shape_manager.get_selected_edit_box() is not None:
                    return

            self.show_prop_of(self.shape_manager.get_selected_shape())
        elif event.button == 2:
            self.shape_manager.select_document_area_box()
        self.redraw()

    def on_drawing_area_mouse_release(self, widget, event):
        self.shape_manager.end_movement()
        self.drawing_area_mouse_pressed = False
        self.show_prop_of(self.shape_manager.get_selected_shape())
        self.update_drawing_area_scrollbars()
        self.redraw()

    def on_drawing_area_mouse_move(self, widget, event):
        self.mouse_point.x = event.x
        self.mouse_point.y = event.y
        if self.drawing_area_mouse_pressed or self.shape_manager.shape_creator is not None:
            doc_start_point, shape_start_point = self.get_doc_and_multi_shape_point(self.mouse_init_point)
            doc_end_point, shape_end_point = self.get_doc_and_multi_shape_point(self.mouse_point)
            self.shape_manager.move_active_item(
                    doc_start_point, doc_end_point, shape_start_point, shape_end_point)
            self.drawing_area.queue_draw()

    def on_drawing_area_scroll(self, scrollbar, scroll_dir):
        value = scrollbar.get_value()
        w, h = self.get_drawing_area_size()
        self.shape_manager.scroll(value, scroll_dir,w ,h)
        self.redraw()

    def on_drawing_area_mouse_scroll(self, widget, event):
        w, h = self.get_drawing_area_size()

        if self.keyboard_object.control_key_pressed:
            if event.direction == Gdk.ScrollDirection.UP:
                zoom = 1.
            elif event.direction == Gdk.ScrollDirection.DOWN:
                zoom = -1.
            self.shape_manager.zoom(zoom, self.mouse_point,w ,h)
            self.update_drawing_area_scrollbars()
        else:
            if event.direction == Gdk.ScrollDirection.UP:
                value = -1
            elif event.direction == Gdk.ScrollDirection.DOWN:
                value = 1.
            value = self.drawing_area_vadjust.get_step_increment()*value
            value += self.drawing_area_vadjust.get_value()
            self.drawing_area_vadjust.set_value(value)
            self.shape_manager.scroll(self.drawing_area_vadjust.get_value(), "vert", w, h)

        self.redraw()
        return True

    def on_configure_event(self, widget, event):
        w, h = self.get_drawing_area_size()
        if self.shape_manager:
            self.shape_manager.fit_area_in_size(w, h)
            self.update_drawing_area_scrollbars()

    def on_drawing_area_draw(self, widget, ctx):
        ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        ctx.save()
        self.shape_manager.draw(ctx)
        ctx.restore()
        w, h = self.get_drawing_area_size()
        ctx.rectangle(0, 0, w, h)
        ctx.set_source_rgba(*Color.parse("cccccc").get_array())
        ctx.stroke()
