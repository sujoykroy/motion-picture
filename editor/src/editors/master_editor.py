from gi.repository import Gtk, Gdk, GLib
import os, math, cairo
import threading
import Queue
import time

from ..shapes import *
from ..gui_utils import *
from ..gui_utils.debug_window import DebugWindow
from ..time_lines import *

from ..audio_tools import AudioServer

from ..document import Document
from shape_manager import ShapeManager
from shape_editor import ShapeEditor
from time_line_editor import TimeLineEditor
from custom_prop_editor import CustomPropEditor

from .. import settings as Settings
from ..settings import EditingChoice
from camera_viewer import CamerViewerBox, CameraViewerDialog

MODE_NEW_SHAPE_CREATE = "MODE_NEW_SHAPE_CREATE"

class MasterEditor(Gtk.ApplicationWindow):
    DEBUG = False
    DEBUG_WINDOW = None

    def __init__(self, width=800, height=300, title="MotionPicture"):
        Gtk.ApplicationWindow.__init__(self, title=title, resizable=True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(width, height)
        self.connect("key-press-event", self.on_drawing_area_key_press)
        self.connect("key-release-event", self.on_drawing_area_key_release)
        self.connect("delete-event", self.quit)

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

        self.toolbar_container = Gtk.VBox()
        self.root_box.pack_start(self.toolbar_container, expand=False, fill=False, padding=0)

        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.root_box.pack_start(sep, expand=False, fill=False, padding=0)

        self.top_info_bar = Gtk.HBox()
        self.root_box.pack_start(self.top_info_bar, expand=False, fill=False, padding=2)

        editing_label = Gtk.Label()
        editing_label.set_markup(Text.markup(
            color=Settings.TOP_INFO_BAR_TEXT_COLOR, weight="bold",text="Editing :"))
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

        self.paned_box_4 = Gtk.VPaned()
        self.paned_box_3.pack2(self.paned_box_4, resize=True, shrink=True)

        self.time_line_editor = TimeLineEditor(self.update_shape_manager,
                                self.show_time_slice_props, self.keyboard_object, self)
        self.paned_box_1.pack2(self.time_line_editor, resize=True, shrink=True)

        self.left_prop_box = Gtk.VBox()
        left_prop_box_container = Gtk.ScrolledWindow()
        left_prop_box_container.add_with_viewport(self.left_prop_box)

        self.curve_joiner_shape_prop_box = CurveJoinerShapePropBox(
                    self, self.shape_prop_changed, self, self.insert_time_slice)
        self.mimic_shape_prop_box = MimicShapePropBox(
                    self, self.shape_prop_changed, self, self.insert_time_slice)
        self.common_shape_prop_box = CommonShapePropBox(
                    self, self.shape_prop_changed, self, self.insert_time_slice)
        self.rectangle_shape_prop_box = RectangleShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.oval_shape_prop_box = OvalShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.ring_shape_prop_box = RingShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.text_shape_prop_box = TextShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.multi_shape_prop_box = MultiShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.curve_smooth_prop_box = CurveSmoothPropBox(
                    self.recreate_shape_editor, self.get_shape_manager)
        self.image_shape_prop_box = ImageShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.audio_shape_prop_box = AudioShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.video_shape_prop_box = VideoShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.threed_shape_prop_box = ThreeDShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.camera_shape_prop_box = CameraShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.document_shape_prop_box = DocumentShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.custom_shape_prop_box = CustomShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)
        self.curve_point_group_shape_prop_box = CurvePointGroupShapePropBox(
                    self, self.shape_prop_changed, self.insert_time_slice)

        self.shape_form_prop_box = ShapeFormPropBox(self.reselect_selected_shape, self.insert_time_slice)
        self.shape_form_prop_box.parent_window = self
        self.custom_props_box = None

        self.point_group_shape_list_box = PointGroupShapeListBox(self.select_point_group_shape)
        self.interior_pose_box = InteriorPoseBox(self.insert_time_slice)

        self.prop_grid = PropGrid()
        self.prop_grid.set_margin_left(10)
        self.prop_grid.set_margin_right(10)
        self.prop_grid.set_margin_bottom(10)

        self.new_custom_prop_button = Gtk.Button("Add Custom Prop")
        self.new_custom_prop_button.connect("clicked", self.new_custom_prop_button_clicked)
        self.prop_grid.add(self.new_custom_prop_button)

        self.linked_to_label = Gtk.Label()
        self.linked_to_hbox = Gtk.HBox()
        self.linked_to_hbox.pack_start(
                Document.create_image("linked_to"),
                expand=False, fill=False, padding=0)
        self.linked_to_hbox.pack_start(self.linked_to_label, expand=False, fill=False, padding=10)
        self.prop_grid.add(self.linked_to_hbox)
        self.prop_grid.add_all(
            self.curve_joiner_shape_prop_box,
            self.mimic_shape_prop_box,
            self.point_group_shape_list_box,
            self.common_shape_prop_box,
            self.rectangle_shape_prop_box,
            self.oval_shape_prop_box,
            self.ring_shape_prop_box,
            self.multi_shape_prop_box,
            self.text_shape_prop_box,
            self.shape_form_prop_box,
            self.curve_smooth_prop_box,
            self.image_shape_prop_box,
            self.audio_shape_prop_box,
            self.video_shape_prop_box,
            self.threed_shape_prop_box,
            self.camera_shape_prop_box,
            self.document_shape_prop_box,
            self.custom_shape_prop_box,
            self.curve_point_group_shape_prop_box,
            self.interior_pose_box
        )
        self.left_prop_box.pack_start(self.prop_grid, expand=True, fill=True, padding=0)
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

        self.drawing_area_vadjust = Gtk.Adjustment(0, 0, 1., .01, 0, 0)
        self.drawing_area_vscrollbar = Gtk.VScrollbar(self.drawing_area_vadjust)
        self.drawing_area_vscrollbar.connect("value-changed", self.on_drawing_area_scroll, "vert")

        self.drawing_area_hadjust = Gtk.Adjustment(0, 0, 1., .01, 0, 0)
        self.drawing_area_hscrollbar = Gtk.HScrollbar(self.drawing_area_hadjust)
        self.drawing_area_hscrollbar.connect("value-changed", self.on_drawing_area_scroll, "horiz")

        drawing_area_container = Gtk.VBox()

        drawing_area_container_tbox = Gtk.HBox()
        drawing_area_container.pack_start(
                drawing_area_container_tbox, expand=True, fill=True, padding=0)
        drawing_area_container.pack_start(
                self.drawing_area_hscrollbar, expand=False, fill=True, padding=0)

        drawing_area_container_tbox.pack_start(self.drawing_area, expand=True,  fill=True, padding=0)
        drawing_area_container_tbox.pack_start(
                    self.drawing_area_vscrollbar, expand=False, fill=True, padding=0)

        self.paned_box_3.pack1(drawing_area_container, resize=True, shrink=True)

        self.right_prop_box = Gtk.VBox()
        right_prop_box_container = Gtk.ScrolledWindow()
        right_prop_box_container.set_name("rightpropbox")
        right_prop_box_container.add_with_viewport(self.right_prop_box)
        self.paned_box_4.pack2(right_prop_box_container, resize=True, shrink=True)

        self.shape_hierarchy = Gtk.VBox()

        self.back_to_parent_shape = Gtk.Button()
        self.back_to_parent_shape.set_image(Document.create_image("back_to_parent", size=20))
        self.back_to_parent_shape.connect("clicked", self.pop_back_to_parent_shape)
        self.shape_hierarchy.pack_end(self.back_to_parent_shape, expand=False, fill=False, padding=0)

        self.multi_shape_tree_container = Gtk.ScrolledWindow()
        self.multi_shape_tree_view = MultiShapeTreeView(self.select_shapes, self.redraw)
        self.multi_shape_tree_container.add_with_viewport(self.multi_shape_tree_view)
        self.shape_hierarchy.pack_start(self.multi_shape_tree_container, expand=True, fill=True, padding=0)

        self.paned_box_4.pack1(self.shape_hierarchy, resize=True, shrink=True)
        self.multi_shape_tree_container.set_size_request(-1, 50)

        self.multi_shape_internal_prop_box = MultiShapeInternalPropBox(
                            self.multi_shape_inter_prop_box_callback,
                            self.load_multi_shape_time_line, self.insert_time_slice)
        self.right_prop_box.pack_start(
                self.multi_shape_internal_prop_box, expand=False, fill=False, padding=0)
        self.multi_shape_internal_prop_box.parent_window = self

        self.time_slice_prop_box = TimeSlicePropBox(self.time_line_editor.update)
        self.right_prop_box.pack_start(self.time_slice_prop_box, expand=False, fill=False, padding=0)

        self.camera_viewer_dialog = None
        AudioShape.AUDIO_ICON = Document.get_icon_shape("audio", 20, 20)
        AVBase.DONT_PLAY_AUDIO = False
        VideoShape.USE_IMAGE_THREAD = True
        CameraShape.CAMERA_ICON = Document.get_icon_shape("camera", 20, 20)

        self.area_fitted = False
        self.img_surf = None
        self.img_surf_lock = threading.RLock()
        self.drawer_thread = None

    def quit(self, widget, event):
        self.time_line_editor.cleanup()

        if self.drawer_thread:
            self.drawer_thread.should_exit = True
            self.drawer_thread.join()

        if self.shape_manager:
            self.shape_manager.cleanup()
        AudioServer.close_all()
        self.hide_camera_viewer()
        Gtk.main_quit()

    def on_quit_camera_view(self):
        self.lookup_action("toggle_camera_viewer").activate(GLib.Variant.new_boolean(False))

    def show_camera_viewer(self):
        if not self.camera_viewer_dialog:
            self.camera_viewer_dialog = CameraViewerDialog(self)
            self.camera_viewer_dialog.set_modal(False)

    def hide_camera_viewer(self):
        if self.camera_viewer_dialog:
            self.camera_viewer_dialog.destroy()
            self.camera_viewer_dialog = None

    def init_interface(self):
        self.show_prop_of(None)
        self.show_time_slice_props(None)

        self.paned_box_2.set_position(185)#left-side-pane, contains shape-props
        self.paned_box_3.set_position(75)#right-side-pane, contains time-slice-props
        self.paned_box_1.set_position(180)
        self.paned_box_4.set_position(20)

        self.open_document(None)

        if self.DEBUG and not MasterEditor.DEBUG_WINDOW:
            MasterEditor.DEBUG_WINDOW = DebugWindow(self)
        self.redraw()

    def set_panel_sizes(self, left, right, bottom):
        self.paned_box_2.set_position(float(left))
        self.paned_box_3.set_position(float(right))
        self.paned_box_1.set_position(float(bottom))

    def show_filename(self):
        filename = self.doc.filename
        if not filename:
            filename = "Untitled"
        else:
            filename = os.path.basename(filename)
        self.set_title("MotionPicture-{0}".format(filename))

    def add_new_action_button(self, name, click_callback, parent_box):
        button = Gtk.Button(name)
        parent_box.pack_start(button, expand = False, fill= False, padding = 5)
        button.connect("clicked", click_callback)

    def get_drawing_area_size(self):
        w = self.drawing_area.get_allocated_width()
        h = self.drawing_area.get_allocated_height()
        return w, h

    def get_doc_and_multi_shape_point(self, point):
        doc_point = self.shape_manager.document_area_box.transform_point(point)
        shape_point = self.multi_shape_stack[-1].transform_locked_shape_point(
                doc_point, root_shape=self.shape_manager.document_area_box, exclude_last=False)
        return doc_point, shape_point

    def load_multi_shape(self, multi_shape, recreate_shape_manager=False):
        if multi_shape not in self.multi_shape_stack:
            self.multi_shape_stack.append(multi_shape)
        if not recreate_shape_manager and self.shape_manager and \
            self.shape_manager.doc.filename == self.doc.filename:
            self.shape_manager.load_multi_shape(multi_shape)
        else:
            self.shape_manager = ShapeManager(multi_shape, self.doc)
            w, h = self.get_drawing_area_size()
            self.shape_manager.document_area_box.move_to(w*.5, h*.5)
            self.shape_manager.resize_scollable_area(w, h)
            self.fit_shape_manager_in_drawing_area()

        self.show_prop_of(None)
        self.load_multi_shape_time_line(None)

        shape_info = ".".join(get_hierarchy_names(multi_shape))
        self.multi_shape_name_label.set_markup(
            Text.markup(shape_info, color=Settings.TOP_INFO_BAR_TEXT_COLOR, weight="bold")
        )
        self.multi_shape_tree_view.set_multi_shape(multi_shape)
        self.multi_shape_internal_prop_box.set_multi_shape(multi_shape)
        if multi_shape.timelines and False:
            timeline_names = multi_shape.timelines.keys()
            if len(timeline_names) == 1 and multi_shape==self.doc.main_multi_shape:
                timeline_name = timeline_names[0]
                self.multi_shape_internal_prop_box.set_timeline(timeline_name)
                self.load_multi_shape_time_line(multi_shape.timelines[timeline_name])
            else:
                self.load_multi_shape_time_line(None)
        self.redraw(use_thread=False)

    def load_multi_shape_time_line(self, multi_shape_time_line):
        self.time_line_editor.set_multi_shape_time_line(multi_shape_time_line)
        self.show_time_slice_props(None)

    def open_document(self, filename=None, width=400., height=400.):
        self.doc = Document(filename, width=width, height=height)
        del self.multi_shape_stack[:]
        self.load_multi_shape(self.doc.get_main_multi_shape(), recreate_shape_manager=True)
        self.show_filename()
        self.area_fitted  = False
        self.fit_shape_manager_in_drawing_area()

    def set_shape_creation_mode(self, shape_type):
        self.next_new_shape_type = shape_type
        self.state_mode = MODE_NEW_SHAPE_CREATE
        return True

    def insert_time_slice(self, shape, prop_name, start_value, end_value=None, prop_data=None, duration=None):
        if not self.time_line_editor.time_line: return
        if duration is None:
            duration = .5
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
        time_line = self.time_line_editor.time_line
        if time_line:
            self.time_slice_prop_box.set_time_markers(time_line.get_time_marker_names())
        self.time_slice_prop_box.set_time_slice_box(time_slice_box)

    def set_shape_name(self, shape, name):
        ret = self.shape_manager.rename_shape(shape, name)
        self.rebuild_tree_view()
        return ret

    def new_custom_prop_button_clicked(self, widget):
        prop_editor = CustomPropEditor(parent=self, shape=self.shape_manager.multi_shape)
        prop_editor.run()
        prop_editor.destroy()
        if self.custom_props_box:
            self.prop_grid.remove_item(self.custom_props_box)
            self.custom_props_box = None
        self.show_prop_of(None)

    def edit_custom_prop(self, prop_name):
        multi_shape = self.shape_manager.multi_shape
        custom_prop = multi_shape.get_custom_prop(prop_name)
        if not custom_prop:
            return
        prop_editor = CustomPropEditor(parent=self, shape=multi_shape)
        prop_editor.set_custom_prop(custom_prop)
        prop_editor.run()
        prop_editor.destroy()
        if self.custom_props_box:
            self.prop_grid.remove_item(self.custom_props_box)
            self.custom_props_box = None
        self.show_prop_of(None)

    def remove_custom_props_box(self):
        if self.custom_props_box:
            self.prop_grid.remove_item(self.custom_props_box)
            self.custom_props_box = None

    def add_custom_props_box(self, multi_shape):
        if multi_shape.custom_props and not self.custom_props_box:
            self.custom_props_box = CustomPropsBox(
                    self, self.redraw,
                    self.insert_time_slice,
                    self.edit_custom_prop,
                    shape=multi_shape)
            self.prop_grid.add(self.custom_props_box)

    def show_prop_of(self, shape):
        self.curve_joiner_shape_prop_box.hide()
        self.mimic_shape_prop_box.hide()
        self.common_shape_prop_box.hide()
        self.rectangle_shape_prop_box.hide()
        self.oval_shape_prop_box.hide()
        self.ring_shape_prop_box.hide()
        self.multi_shape_prop_box.hide()
        self.shape_form_prop_box.hide()
        self.point_group_shape_list_box.hide()
        self.curve_smooth_prop_box.hide()
        self.text_shape_prop_box.hide()
        self.image_shape_prop_box.hide()
        self.video_shape_prop_box.hide()
        self.audio_shape_prop_box.hide()
        self.camera_shape_prop_box.hide()
        self.threed_shape_prop_box.hide()
        self.document_shape_prop_box.hide()
        self.custom_shape_prop_box.hide()
        self.new_custom_prop_button.hide()
        self.curve_point_group_shape_prop_box.hide()
        self.interior_pose_box.hide()
        self.remove_custom_props_box()

        if shape != None:
            if shape.linked_to:
                self.linked_to_label.set_text(".".join(get_hierarchy_names(shape.linked_to)))
                self.linked_to_hbox.show()
            else:
                self.linked_to_hbox.hide()

            if isinstance(shape, CurveJoinerShape):
                self.curve_joiner_shape_prop_box.set_prop_object(shape)
                self.curve_joiner_shape_prop_box.show()
                return

            if isinstance(shape, MimicShape):
                self.mimic_shape_prop_box.set_prop_object(shape)
                self.mimic_shape_prop_box.show()
                return

            self.common_shape_prop_box.show()
            self.common_shape_prop_box.set_prop_object(shape)

            if isinstance(shape, TextShape):
                self.text_shape_prop_box.show()
                self.text_shape_prop_box.set_prop_object(shape)

            if isinstance(shape, AudioShape):
                self.audio_shape_prop_box.show()
                self.audio_shape_prop_box.set_prop_object(shape)

            if isinstance(shape, VideoShape):
                self.video_shape_prop_box.show()
                self.video_shape_prop_box.set_prop_object(shape)

            if isinstance(shape, CameraShape):
                self.camera_shape_prop_box.show()
                self.camera_shape_prop_box.set_prop_object(shape)

            if isinstance(shape, ThreeDShape):
                self.threed_shape_prop_box.show()
                self.threed_shape_prop_box.set_prop_object(shape)

            if isinstance(shape, CurvePointGroupShape):
                self.curve_point_group_shape_prop_box.show()
                self.curve_point_group_shape_prop_box.set_prop_object(shape)

            if isinstance(shape, CustomShape):
                self.custom_shape_prop_box.show()
                self.custom_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, DocumentShape):
                self.document_shape_prop_box.show()
                self.document_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, ImageShape):
                self.image_shape_prop_box.show()
                self.image_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, RectangleShape):
                self.rectangle_shape_prop_box.show()
                self.rectangle_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, RingShape):
                self.ring_shape_prop_box.show()
                self.ring_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, OvalShape):
                self.oval_shape_prop_box.show()
                self.oval_shape_prop_box.set_prop_object(shape)
            elif isinstance(shape, MultiShape):
                self.multi_shape_prop_box.show()
                self.multi_shape_prop_box.set_prop_object(shape)
                self.add_custom_props_box(shape)
            elif isinstance(shape, CurveShape) or isinstance(shape, PolygonShape):
                self.shape_form_prop_box.show()
                self.shape_form_prop_box.set_curve_shape(shape)

            if isinstance(shape, CurveShape):
                self.curve_smooth_prop_box.set_curve_shape(shape)
                self.curve_smooth_prop_box.show()

            if isinstance(shape, CurveShape) or \
               isinstance(shape, CurvePointGroupShape):
                if isinstance(shape, CurvePointGroupShape):
                    curve_shape = shape.parent_shape
                else:
                    curve_shape = shape
                self.point_group_shape_list_box.set_shape_list(
                    curve_shape.get_point_group_shapes_model())
                self.point_group_shape_list_box.show()

            if shape.has_poses():
                self.interior_pose_box.set_shape(shape)
                self.interior_pose_box.show()
        else:
            self.linked_to_hbox.hide()
            self.shape_form_prop_box.set_curve_shape(None)
            self.new_custom_prop_button.show()

            if not self.custom_props_box and self.shape_manager:
                multi_shape = self.shape_manager.multi_shape
                self.add_custom_props_box(multi_shape)

    def shape_prop_changed(self, widget):
        #shape = self.shape_manager.get_deepest_selected_shape()
        self.redraw()

    def select_shapes(self, shapes, double_clicked=False):
        if double_clicked and len(shapes)==1 and \
            isinstance(shapes[0], MultiShape) and shapes[0].get_is_designable():
            self.load_multi_shape(shapes[0])
        #elif len(shapes) == 1 and shapes[0] is None and double_clicked:
        #    self.pop_back_to_parent_shape()
        else:
            self.shape_manager.select_shapes(shapes)
            if len(shapes) == 1:
                self.show_prop_of(shapes[0])
                self.time_line_editor.set_selected_shape(shapes[0])
        self.redraw()

    def select_point_group_shape(self, point_group_shape):
        if point_group_shape:
            self.shape_manager.select_point_group_shape(point_group_shape)
        else:
            self.shape_manager.delete_point_group_shape_editor()
        self.show_prop_of(self.shape_manager.get_deepest_selected_shape())
        self.redraw()

    def reselect_selected_shape(self):
        shape = self.shape_manager.get_selected_shape(True)
        if shape:
            self.shape_manager.select_shape(shape)
        self.redraw()

    def update_drawing_area_scrollbars(self):
        w, h = self.get_drawing_area_size()
        #self.shape_manager.resize_scollable_area(w, h)
        x_pos, y_pos = self.shape_manager.get_scroll_position(w, h)
        self.drawing_area_vadjust.set_value(y_pos)
        self.drawing_area_hadjust.set_value(x_pos)

    def update_shape_manager(self):
        self.shape_manager.update()
        self.pre_draw_on_surface()
        self.redraw(use_thread=False)

    def recreate_shape_editor(self):
        if self.shape_manager.shape_editor:
            self.shape_manager.shape_editor = ShapeEditor(self.shape_manager.shape_editor.shape)
        self.redraw()

    def get_shape_manager(self):
        return self.shape_manager

    def multi_shape_inter_prop_box_callback(self):
        self.rebuild_tree_view()
        self.redraw()

    def rebuild_tree_view(self):
        self.multi_shape_tree_view.rebuild()

    def redraw(self, use_thread=True):
        if self.drawer_thread and use_thread:
            self.drawer_thread.draw()
        else:
            self.drawing_area.queue_draw()
        if self.camera_viewer_dialog:
            self.camera_viewer_dialog.redraw()
        return self.playing

    def pop_back_to_parent_shape(self, widget=None):
        if len(self.multi_shape_stack)<=1:
            return
        del self.multi_shape_stack[-1]
        multi_shape = self.multi_shape_stack[-1]
        del self.multi_shape_stack[-1]
        self.remove_custom_props_box()
        self.load_multi_shape(multi_shape)

    def on_drawing_area_key_press(self, widget, event):
        self.keyboard_object.set_keypress(event.keyval, pressed=True)

    def on_drawing_area_key_release(self, widget, event):
        self.keyboard_object.set_keypress(event.keyval, pressed=False)

    def on_drawing_area_mouse_press(self, widget, event):
        self.mouse_init_point.x = self.mouse_point.x
        self.mouse_init_point.y = self.mouse_point.y
        self.drawing_area_mouse_pressed = True
        if event.button == 1:#Left mouse
            if event.type == Gdk.EventType._2BUTTON_PRESS:#double button click
                double_click_handled = True
                if self.shape_manager.has_shape_creator():
                    self.shape_manager.complete_shape_creation()
                    self.rebuild_tree_view()
                elif self.shape_manager.has_designable_multi_shape_selected():
                    multi_shape = self.shape_manager.get_selected_shape()
                    self.load_multi_shape(multi_shape)
                elif self.shape_manager.color_editor:
                    doc_point, shape_point = self.get_doc_and_multi_shape_point(self.mouse_point)
                    self.shape_manager.double_click_in_color_editor(shape_point)
                elif self.shape_manager.selected_shape_supports_point_insert():
                    doc_point, shape_point = self.get_doc_and_multi_shape_point(self.mouse_point)
                    self.shape_manager.insert_point_in_shape_at(shape_point)
                elif self.shape_manager.has_no_shape_selected():
                    if len(self.multi_shape_stack)>1:
                        self.pop_back_to_parent_shape()
                    else:
                        double_click_handled = False
                if double_click_handled:
                    return

            if self.state_mode == MODE_NEW_SHAPE_CREATE and self.shape_manager.shape_creator is None:
                    doc_point, shape_point = self.get_doc_and_multi_shape_point(self.mouse_point)
                    self.shape_manager.start_creating_new_shape(
                                    self.next_new_shape_type, doc_point, shape_point)
                    self.state_mode = None
                    self.lookup_action("create_new_shape").activate(GLib.Variant.new_string(""))
            else:
                self.shape_manager.select_item_at(self.mouse_point.copy(),
                        multi_select=self.keyboard_object.shift_key_pressed,
                        box_select=self.keyboard_object.control_key_pressed)
                self.time_line_editor.set_selected_shape(self.shape_manager.get_selected_shape())
                if self.shape_manager.get_selected_edit_box() is not None:
                    return
            self.show_prop_of(self.shape_manager.get_deepest_selected_shape())
        elif event.button == 3:
            self.shape_manager.select_document_area_box()
        self.redraw()

    def on_drawing_area_mouse_release(self, widget, event):
        had_shape_creator = (self.shape_manager.shape_creator is not None)
        self.shape_manager.end_movement()
        self.drawing_area_mouse_pressed = False
        self.show_prop_of(self.shape_manager.get_deepest_selected_shape())
        self.update_drawing_area_scrollbars()
        if had_shape_creator:
            self.rebuild_tree_view()
        self.redraw()

    def on_drawing_area_mouse_move(self, widget, event):
        self.mouse_point.x = event.x
        self.mouse_point.y = event.y

        if self.drawing_area_mouse_pressed or self.shape_manager.shape_creator is not None:
            self.shape_manager.move_active_item(self.mouse_init_point.copy(), self.mouse_point.copy())
            self.redraw()

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
            value /= self.shape_manager.get_scale()
            value += self.drawing_area_vadjust.get_value()
            self.drawing_area_vadjust.set_value(value)
            self.shape_manager.scroll(self.drawing_area_vadjust.get_value(), "vert", w, h)

        self.redraw()
        return True

    def fit_shape_manager_in_drawing_area(self):
        w, h = self.get_drawing_area_size()
        if self.shape_manager:
            if not self.area_fitted:
                self.shape_manager.fit_area_in_size(w, h)
                self.area_fitted = True
            else:
                self.shape_manager.resize_area(w, h)
            self.update_drawing_area_scrollbars()

    def on_configure_event(self, widget, event):
        self.fit_shape_manager_in_drawing_area()
        w, h = self.get_drawing_area_size()
        self.img_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.pre_draw_on_surface()
        self.redraw(use_thread=False)

    def pre_draw_on_surface(self):
        self.img_surf_lock.acquire()
        ctx = cairo.Context(self.img_surf)
        ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

        w = self.img_surf.get_width()
        h = self.img_surf.get_height()

        ctx.rectangle(0, 0, w, h)
        ctx.set_source_rgba(*Color.parse("eeeeee").get_array())
        ctx.fill()

        if self.shape_manager:
            ctx.save()
            area = Point(float(w),float(h))
            self.shape_manager.draw(ctx, area)
            ctx.restore()

        ctx.rectangle(0, 0, w, h)
        ctx.set_source_rgba(*Color.parse("cccccc").get_array())
        ctx.stroke()
        self.img_surf_lock.release()

    def on_drawing_area_draw(self, widget, dctx):
        if not self.drawer_thread:
            self.pre_draw_on_surface()
            self.drawer_thread = DrawerThread(self)
        self.img_surf_lock.acquire()
        dctx.set_source_surface(self.img_surf)
        dctx.paint()
        self.img_surf_lock.release()

class DrawerThread(threading.Thread):
    def __init__(self, editor):
        super(DrawerThread, self).__init__()
        self.editor = editor
        self.should_exit = False
        self.draw_queue = Queue.Queue()
        self.start()

    def draw(self):
        self.draw_queue.put(True)

    def run(self):
        while not self.should_exit:
            draw = False
            try:
                st = time.time()
                while time.time()-st<.1:
                    ret = self.draw_queue.get(block=False)
                    draw = True
            except Queue.Empty:
                pass
            if draw:
                self.editor.pre_draw_on_surface()
                self.editor.redraw(use_thread=False)
            time.sleep(.01)
