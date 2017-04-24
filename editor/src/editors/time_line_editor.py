from gi.repository import Gtk, GObject, Gdk
import time

from ..commons import *
from ..commons.draw_utils import *
from ..time_lines import MultiShapeTimeLine
from ..time_line_boxes import *

from ..gui_utils import buttons, YesNoDialog
from ..settings import EditingChoice
from .. import settings as Settings

EDITOR_LINE_COLOR = "ff0000"
TIME_SLICE_START_X = PropTimeLineBox.TOTAL_LABEL_WIDTH + SHAPE_LINE_LEFT_PADDING
MOVE_TO_INCREMENT = .1

class PlayHeadBox(RectBox):
    def __init__(self, play_head_callback):
       RectBox.__init__(self, parent_box=None, width=50, height=1,
                        border_color="000000", border_width=1, fill_color="65737255")
       self.play_head_callback = play_head_callback

    def get_center_x(self):
        return self.left + self.width*.5

    def set_center_x(self, x):
        self.left = x - self.width*.5

    def draw(self, ctx):
        RectBox.draw(self, ctx)
        ctx.save()
        self.pre_draw(ctx)
        cx = self.width*.5
        draw_straight_line(ctx, cx, 0, cx, self.height)
        ctx.restore()
        draw_stroke(ctx, self.border_width, self.border_color)

    def move_to(self, point, move_to_callback):
        Box.move_to(self, Point(point.x, self.top))
        self.play_head_callback()

class TimeMarkerBox(RectBox):
    def __init__(self, time_marker):
        RectBox.__init__(self, parent_box=None, width=10, height=TIME_STAMP_LABEL_HEIGHT,
                        border_color="000000", border_width=1, fill_color="65737255")
        self.time_marker = time_marker

    def set_x(self, x):
        self.left = x

    def get_x(self):
        return self.left

    def move_to(self, point, move_to_callback):
        Box.move_to(self, Point(point.x, self.top))

class TimeRange(object):
    def __init__(self):
        self._start_pixel = 0
        self._visible_duration_pixel = 0
        self._non_scaled_full_length_pixel = 0
        self.scaled_full_length_pixel = 0
        self._scale = 1.
        self.pixel_per_second = PIXEL_PER_SECOND
        self.visible_span = Span(0, 0, 1)

    def reset(self):
        self._scale = 1.
        self.pixel_per_second = PIXEL_PER_SECOND
        self.scaled_full_length_pixel = self._visible_duration_pixel
        self._start_pixel = 0

    def set_visible_duration_pixel(self, duration_pixel):
        self._visible_duration_pixel = duration_pixel

    def increse_scale(self, scale_incre, abs_mouse_point):
        self._scale *= (1+scale_incre)
        mouse_offset_x = abs_mouse_point.x - TIME_SLICE_START_X
        current_mouse_time_pixel = mouse_offset_x+self._start_pixel
        current_mouse_time = current_mouse_time_pixel/self.pixel_per_second
        self.pixel_per_second = PIXEL_PER_SECOND*self._scale
        self._calculate()
        new_mouse_time_pixel = current_mouse_time*self.pixel_per_second
        self._start_pixel = (new_mouse_time_pixel - mouse_offset_x)

        excess_length = self.scaled_full_length_pixel-self._visible_duration_pixel
        if self._start_pixel>excess_length:
            self._start_pixel = excess_length
        if self._start_pixel<0:
            self._start_pixel = 0

    def set_non_scaled_full_length_pixel(self, pixel):
        self._non_scaled_full_length_pixel = pixel
        self._calculate()

    def _calculate(self):
        self.scaled_full_length_pixel = self._non_scaled_full_length_pixel*self._scale

    def get_scroll_position(self):
        excess_length = self.scaled_full_length_pixel-self._visible_duration_pixel
        return self._start_pixel/excess_length

    def scroll_to(self, frac):
        excess_length = self.scaled_full_length_pixel-self._visible_duration_pixel
        if excess_length<0: excess_length = 0
        self._start_pixel = excess_length*frac

    def get_start_end_time(self):
        self.visible_span.start = self._start_pixel/self.pixel_per_second
        self.visible_span.end = (self._start_pixel+self._visible_duration_pixel)/self.pixel_per_second
        self.visible_span.scale = self._scale
        return self.visible_span

    def get_start_pixel(self):
        return self._start_pixel

    def get_scale(self):
        return self._scale

    def get_visible_duration_pixel (self):
        return self._visible_duration_pixel

    def get_time_for_extra_x(self, x):
        return (x+self._start_pixel)/self.pixel_per_second

    def get_extra_pixel_for_time(self, time_value):
        time_pixel = time_value*self.pixel_per_second
        return time_pixel - self._start_pixel

    def get_seconds_per_pixel(self):
        return 1./(PIXEL_PER_SECOND*self._scale)

class TimeMarkerEditDialog(Gtk.Dialog):
    MARKER_SAVED = 1000
    DELETE_MARKER = 2000

    def __init__(self, parent, title, time_marker, width=400, height=50):
        Gtk.Dialog.__init__(self, title, parent, 0)
        self.set_default_size(width, height)
        self.time_marker= time_marker
        box = self.get_content_area()

        label_box = Gtk.Box(orientation=0)
        box.pack_start(label_box, expand=False, fill=False, padding= 10)

        text_label = Gtk.Label("Label")
        label_box.pack_start(text_label, expand=False, fill=False, padding=10)
        self.text_entry = Gtk.Entry()
        self.text_entry.set_text(time_marker.text)
        label_box.pack_start(self.text_entry, expand=True, fill=True, padding=10)

        at_label = Gtk.Label("At")
        label_box.pack_start(at_label, expand=False, fill=False, padding=10)
        self.at_entry = Gtk.Entry()
        self.at_entry.set_text("{0}".format(time_marker.at))
        label_box.pack_start(self.at_entry, expand=True, fill=True, padding=10)

        button_box = Gtk.Box(orientation=0)
        box.pack_end(button_box, expand=False, fill=False, padding=10)

        save_button = Gtk.Button("Save")
        save_button.connect("clicked", self.save_button_clicked)
        button_box.pack_start(save_button, expand=False, fill=False, padding=10)
        cancel_button = Gtk.Button("Cancel")
        button_box.pack_start(cancel_button, expand=False, fill=False, padding=0)
        cancel_button.connect("clicked", self.cancel_button_clicked)

        delete_button = Gtk.Button("Delete")
        button_box.pack_end(delete_button, expand=False, fill=False, padding=10)
        delete_button.connect("clicked", self.delete_button_clicked)

        self.show_all()

    def save_button_clicked(self, widget):
        self.time_marker.set_text(self.text_entry.get_text())
        self.time_marker.set_at(self.at_entry.get_text())
        self.response(TimeMarkerEditDialog.MARKER_SAVED)

    def cancel_button_clicked(self, widget):
        self.response(Gtk.ResponseType.NONE)

    def delete_button_clicked(self, widget):
        self.response(TimeMarkerEditDialog.DELETE_MARKER)

class TimeLineEditor(Gtk.VBox):
    def __init__(self, play_head_callback, time_slice_box_select_callback, keyboard_object, parent_window):
        Gtk.VBox.__init__(self)

        self.keyboard_object = keyboard_object
        self.play_head_callback = play_head_callback
        self.time_slice_box_select_callback = time_slice_box_select_callback
        self.parent_window = parent_window

        info_hbox = Gtk.HBox()
        self.pack_start(info_hbox, expand=False, fill=False, padding=0)

        self.drawing_area = Gtk.DrawingArea()

        self.drawing_area_vadjust = Gtk.Adjustment(0, 0, 1., .1, 0, 0)
        self.drawing_area_vscrollbar = Gtk.VScrollbar(self.drawing_area_vadjust)
        self.drawing_area_vscrollbar.connect("value-changed",
                            self.on_drawing_area_scrollbar_value_changed, "vert")

        self.drawing_area_hadjust = Gtk.Adjustment(0, 0, 1., .01, 0, 0)
        self.drawing_area_hscrollbar = Gtk.HScrollbar(self.drawing_area_hadjust)
        self.drawing_area_hscrollbar.connect("value-changed",
                            self.on_drawing_area_scrollbar_value_changed, "horiz")

        drawing_area_container_tbox = Gtk.HBox()
        self.pack_start(drawing_area_container_tbox, expand=True,  fill=True, padding=0)
        self.pack_start(self.drawing_area_hscrollbar, expand=False,  fill=True, padding=0)

        drawing_area_container_tbox.pack_start(self.drawing_area, expand=True,  fill=True, padding=0)
        drawing_area_container_tbox.pack_start(self.drawing_area_vscrollbar,
                                expand=False,  fill=True, padding=0)

        self.drawing_area.set_events(
            Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK|\
            Gdk.EventMask.BUTTON_RELEASE_MASK|Gdk.EventMask.SCROLL_MASK)

        self.drawing_area.connect("draw", self.on_drawing_area_draw)
        self.drawing_area.connect("configure-event", self.on_configure_event)
        self.drawing_area.connect("button-press-event", self.on_drawing_area_mouse_press)
        self.drawing_area.connect("button-release-event", self.on_drawing_area_mouse_release)
        self.drawing_area.connect("motion-notify-event", self.on_drawing_area_mouse_move)
        self.drawing_area.connect("scroll-event", self.on_drawing_area_mouse_scroll)

        self.time_line_name_label = Gtk.Label()
        info_hbox.pack_start(self.time_line_name_label, expand=False, fill=False, padding=5)

        self.play_head_time_label = Gtk.Label()
        self.play_head_time_label.set_size_request(100, -1)
        info_hbox.pack_end(self.play_head_time_label, expand=False, fill=False, padding=5)

        self.play_button = buttons.create_new_image_button("play")
        self.play_button.connect("clicked", self.on_play_pause_button_click, True)
        info_hbox.pack_end(self.play_button, expand=False, fill=False, padding=5)
        self.pause_button = buttons.create_new_image_button("pause")
        self.pause_button.connect("clicked", self.on_play_pause_button_click, False)
        info_hbox.pack_end(self.pause_button, expand=False, fill=False, padding=5)


        self.multi_shape_time_line_box = None

        self.mouse_pressed = False
        self.mouse_point = Point(0, 0)
        self.mouse_init_point = Point(0, 0)

        self.selected_item = None
        self.init_selected_item = Box()
        self.selected_time_slice_box = None

        self.play_head_box = None
        self.play_head_time = 0.

        self.inner_box = Box()
        self.inner_box.left = PROP_NAME_LABEL_WIDTH + \
                              PROP_VALUE_LABEL_WIDTH + 4*PROP_NAME_LABEL_RIGHT_PADDING
        self.inner_box.top = 0
        self.time_range = TimeRange()
        self.mouse_position_box = RectBox(None, width=1, height=1,
                        border_color="0000ff", border_width=1, fill_color="ff0000")
        self.mouse_time_position = 0

        self.is_playing = False
        self.last_play_updated_at = 0
        self.selected_shape = None

        self.time_marker_boxes = dict()

    def set_multi_shape_time_line(self, multi_shape_time_line):
        self.time_line = multi_shape_time_line
        self.time_marker_boxes = dict()
        self.selected_time_slice_box = None
        self.is_playing = False
        self.last_play_updated_at = 0
        self.selected_shape = None
        if multi_shape_time_line == None:
            self.time_line_name_label.set_text("")
            self.multi_shape_time_line_box = None
            self.time_range.reset()
            self.play_button.hide()
            self.pause_button.hide()
            self.update()
        else:
            self.time_line_name_label.set_text(self.time_line.name)
            self.time_line_name_label.set_markup(Text.markup(self.time_line.name,
                    color=Settings.TOP_INFO_BAR_TEXT_COLOR, weight="bold"))
            self.time_line.get_duration()
            self.multi_shape_time_line_box = MultiShapeTimeLineBox(multi_shape_time_line)

            for time_marker in self.time_line.time_markers.values():
                self.time_marker_boxes[time_marker.at]=TimeMarkerBox(time_marker)

            self.play_head_box = PlayHeadBox(self.on_play_head_move)
            self.play_button.show()
            self.pause_button.hide()
            self.update()
            self.move_play_head_to_time(0)
        self.is_playing = False

    def show_current_play_head_time(self):
        self.play_head_time_label.set_markup(
            "Playhead at: <span color=\"#cc6600\">{0:.2f}</span> sec".format(self.play_head_time))

    def move_play_head_to_time(self, value):
        if value is not None:
            self.play_head_time = value
            self.time_line.move_to(self.play_head_time)
        extra_x = self.time_range.get_extra_pixel_for_time(self.play_head_time)
        if self.play_head_box:
            self.play_head_box.set_center_x(TIME_SLICE_START_X + extra_x)
        self.show_current_play_head_time()

    def get_play_head_time(self):
        if not self.play_head_box: return 0.
        return self.play_head_time

    def set_selected_shape(self, shape):
        if not self.time_line: return
        load_single_shape = None
        if self.time_line.shape_time_lines.key_exists(shape):
            if self.multi_shape_time_line_box.shape_exists(shape):
                if self.multi_shape_time_line_box.get_shape_count()>1:
                    if EditingChoice.SHOW_ALL_TIME_LINES:
                        load_single_shape = None
                    else:
                        load_single_shape = True
            else:
                if EditingChoice.SHOW_ALL_TIME_LINES:
                    load_single_shape = False
                else:
                    load_single_shape = True
        if load_single_shape is True:
            multi_shape_time_line = MultiShapeTimeLine(self.time_line.multi_shape)
            shape_time_line =  self.time_line.shape_time_lines[shape]
            multi_shape_time_line.shape_time_lines.add(shape, shape_time_line)
            self.multi_shape_time_line_box = MultiShapeTimeLineBox(multi_shape_time_line)
            self.multi_shape_time_line_box.update()
        elif load_single_shape is False:
            self.multi_shape_time_line_box = MultiShapeTimeLineBox(self.time_line)

        self.selected_shape = shape
        self.update_prop_lines_time_scale()
        self.update()

    def redraw(self):
        self.drawing_area.queue_draw()

    def select_item_at(self, point):
        if not self.multi_shape_time_line_box: return
        if self.play_head_box.is_within(point):
            self.selected_item = self.play_head_box

        if not self.selected_item:
            tm_point = point.copy()
            tm_point.translate(0, TIME_STAMP_LABEL_HEIGHT)
            for time_marker_box in self.time_marker_boxes.values():
                if time_marker_box.is_within(tm_point):
                    self.selected_item = time_marker_box
                    break

        if not self.selected_item:
            for shape_line_box in self.multi_shape_time_line_box.shape_time_line_boxes:
                for prop_line_box in shape_line_box.prop_time_line_boxes:
                    for time_slice_box in prop_line_box.time_slice_boxes:
                        for edit_box in reversed(time_slice_box.edit_boxes):
                            if edit_box.is_within(point):
                                self.selected_item = edit_box
                                break
        if self.selected_item:
            self.selected_item.copy_into(self.init_selected_item)

    def delete_time_slice(self):
        if not self.selected_time_slice_box: return
        time_slice = self.selected_time_slice_box.time_slice

        prop_time_line_box = self.selected_time_slice_box.prop_time_line_box
        prop_time_line = prop_time_line_box.prop_time_line

        shape_time_line_box = prop_time_line_box.parent_box
        shape_time_line = shape_time_line_box.shape_time_line

        multi_shape_time_line_box = shape_time_line_box.parent_box
        multi_shape_time_line = multi_shape_time_line_box.multi_shape_time_line

        multi_shape_time_line.remove_shape_prop_time_slice(
                shape_time_line.shape, prop_time_line.prop_name, time_slice)
        self.update()
        self.redraw()

    def select_time_slice_box_at(self, point):
        if not self.multi_shape_time_line_box: return
        self.selected_time_slice_box = None
        for shape_line_box in self.multi_shape_time_line_box.shape_time_line_boxes:
            for prop_line_box in shape_line_box.prop_time_line_boxes:
                for time_slice_box in prop_line_box.time_slice_boxes:
                    if time_slice_box.is_within(point):
                        self.selected_time_slice_box = time_slice_box
                        self.selected_time_slice_box.highlighted = True
                        break
        self.on_time_slice_box_select()
        return self.selected_time_slice_box

    def end_movement(self):
        if not self.multi_shape_time_line_box: return
        self.selected_item = None
        self.multi_shape_time_line_box.update()
        self.redraw()

    def move_active_item(self, start_point, end_point):
        if not self.selected_item: return
        if self.selected_item.parent_box:
            start_point = self.selected_item.parent_box.abs_transform_point(start_point)
            end_point = self.selected_item.parent_box.abs_transform_point(end_point)
            diff_point = end_point.diff(start_point)
        else:
            diff_point = end_point.diff(start_point)

        diff_point.translate(self.init_selected_item.left, self.init_selected_item.top)
        self.selected_item.move_to(diff_point, self.on_move_to)

        if isinstance(self.selected_item, TimeMarkerBox):
            time_marker_box = self.selected_item
            time_marker = time_marker_box.time_marker
            extra_x = time_marker_box.get_x()-TIME_SLICE_START_X
            time_to = self.time_range.get_time_for_extra_x(extra_x)
            self.move_time_marker(time_marker, time_marker.at, time_to)
            self.update_time_marker_boxes()
        self.time_line.get_duration()

    def move_time_marker(self, time_marker, old_at, new_at):
        if self.time_line.move_time_marker(old_at, new_at):
            self.time_marker_boxes[new_at] = self.time_marker_boxes[old_at]
            del self.time_marker_boxes[old_at]

    def delete_time_marker(self, time_marker):
        if self.time_line.delete_time_marker(time_marker.at):
            del self.time_marker_boxes[time_marker.at]

    def update(self):
        if self.multi_shape_time_line_box:
            self.multi_shape_time_line_box.update()
            self.time_range.set_non_scaled_full_length_pixel(
                        self.multi_shape_time_line_box.time_line_width)
            self.play_head_box.height = self.drawing_area.get_allocated_height()

            self.update_time_marker_boxes()

        self.mouse_position_box.height = self.drawing_area.get_allocated_height()
        self.redraw()

    def update_prop_lines_time_scale(self):
        scale_x = self.time_range.get_scale()
        for shape_line_box in self.multi_shape_time_line_box.shape_time_line_boxes:
            for prop_line_box in shape_line_box.prop_time_line_boxes:
                prop_line_box.set_time_multiplier(scale_x)

    def update_time_marker_boxes(self):
        for marker_at in self.time_line.time_markers:
            extra_x = self.time_range.get_extra_pixel_for_time(marker_at)
            self.time_marker_boxes[marker_at].set_x(TIME_SLICE_START_X + extra_x)

    def update_slices_left(self):
        if not self.multi_shape_time_line_box:
            return
        self.multi_shape_time_line_box.update_slices_container_box_left(
                PropTimeLineBox.TOTAL_LABEL_WIDTH-self.time_range.get_start_pixel())

    def update_drawing_area_scrollbars(self):
        x_pos = self.time_range.get_scroll_position()
        self.drawing_area_hadjust.set_value(x_pos)

    def time_scroll_to(self, value):
        self.time_range.scroll_to(value)
        self.update_slices_left()
        self.update_time_marker_boxes()

    def zoom_time(self, value):
        self.time_range.increse_scale(value, self.mouse_point)
        if not self.multi_shape_time_line_box:
            return

        self.update_prop_lines_time_scale()
        self.update_time_marker_boxes()

    def zoom_vertical(self, value, point):
        if not self.multi_shape_time_line_box: return
        scale_y = 1+ value

        for shape_line_box in self.multi_shape_time_line_box.shape_time_line_boxes:
            for prop_line_box in shape_line_box.prop_time_line_boxes:
                if prop_line_box.is_within(point):
                    prop_line_box.set_vertical_multiplier(scale_y)
                    break

    def on_play_pause_button_click(self, widget, play):
        if self.time_line.duration == 0:
            self.is_playing = False
        else:
            was_playing = self.is_playing
            if not self.is_playing:
                self.last_play_updated_at = 0
            self.is_playing = play
            if not was_playing:
                self.timer_id = GObject.timeout_add(100, self.on_playing_timer_movement)
        if self.is_playing:
            self.play_button.hide()
            self.pause_button.show()
        else:
            self.play_button.show()
            self.pause_button.hide()

    def on_playing_timer_movement(self):
        current_time = time.time()
        if self.last_play_updated_at>0:
            diff = current_time - self.last_play_updated_at
            diff = MOVE_TO_INCREMENT
            value = self.play_head_time + diff
            if self.time_line.duration == 0:
                value = 0
            elif value > self.time_line.duration:
                value %= self.time_line.duration
            self.move_play_head_to_time(value)
        self.last_play_updated_at = current_time
        self.redraw()
        self.play_head_callback()
        return self.is_playing

    def on_time_slice_box_select(self):
        self.time_slice_box_select_callback(self.selected_time_slice_box)

    def on_play_head_move(self):
        extra_x = self.play_head_box.get_center_x()-TIME_SLICE_START_X
        self.play_head_time = self.time_range.get_time_for_extra_x(extra_x)
        if self.play_head_time<0:
            self.move_play_head_to_time(0)
        self.show_current_play_head_time()
        self.time_line.move_to(self.play_head_time)
        self.play_head_callback()

    def on_move_to(self):
        self.update()

    def on_drawing_area_draw(self, widget, ctx):
        widget_width = widget.get_allocated_width()
        widget_height = widget.get_allocated_height()

        ctx.rectangle(0, 0, widget_width, widget.get_allocated_height())
        draw_fill(ctx, TIME_LINE_BACKGROUND_COLOR)

        active = (self.multi_shape_time_line_box is not None)

        ctx.translate(DRAW_AREA_PADDING, 0)

        #left prop name vertical box background
        ctx.save()
        ctx.rectangle(0, 0, TIME_SLICE_START_X, widget.get_allocated_height())
        draw_fill(ctx, PROP_LEFT_BACK_COLOR)

        visible_time_span = self.time_range.get_start_end_time()
        visible_time_start, visible_time_end = visible_time_span.start, visible_time_span.end

        if active:
            #draw time slices
            ctx.save()
            ctx.translate(0, TIME_STAMP_LABEL_HEIGHT)
            self.multi_shape_time_line_box.draw(ctx, visible_time_span, self.selected_shape)
            ctx.restore()

        #left prop name vertical box, rework to unwind prop_line's back distortions
        ctx.save()
        ctx.rectangle(-DRAW_AREA_PADDING, 0, DRAW_AREA_PADDING, widget_height)
        draw_fill(ctx, TIME_LINE_BACKGROUND_COLOR)
        #left prop name vertical box right line
        ctx.translate(TIME_SLICE_START_X-1, 0)
        draw_straight_line(ctx, 0, 0, 0, widget_height)
        draw_stroke(ctx, 1, EDITOR_LINE_COLOR)
        ctx.restore()
        #left prop name vertical box left line
        draw_straight_line(ctx, 0, 0, 0, widget_height)
        draw_stroke(ctx, 1, EDITOR_LINE_COLOR)
        ctx.restore()

        #Draw time labels
        ctx.save()
        ctx.rectangle(0, 0, widget_width, TIME_STAMP_LABEL_HEIGHT)
        draw_fill(ctx, TIME_LINE_BACKGROUND_COLOR)

        #time_label_gap_unit = 1.
        #printable_time_start = visible_time_start+(time_label_gap_unit-visible_time_start%time_label_gap_unit)
        #time_stamp = printable_time_start

        if self.time_line:
            time_labels = self.time_line.time_labels
        if not self.time_line or not time_labels:
            time_labels = [TimeLabel(start=0, end=-1, step=1.)]
            time_labels.append(TimeLabel(start=0, end=-1, step=1./2, level=1))
            time_labels.append(TimeLabel(start=0, end=-1, step=1./4, level=2))
            time_labels.append(TimeLabel(start=0, end=-1, step=1./8, level=3))

        for time_label in time_labels:
            if self.time_range.pixel_per_second*time_label.step<20:
                continue
            if time_label.start>visible_time_end:
                continue
            if time_label.end>0 and time_label.end<visible_time_start:
                continue
            if time_label.start>visible_time_start:
                printable_time_start = time_label.start
            else:
                printable_time_start = visible_time_start+\
                                   (time_label.step-visible_time_start%time_label.step)
            time_stamp = printable_time_start

            while time_stamp <visible_time_end and \
                  (time_label.end==-1 or time_stamp<time_label.end):
                ctx.save()
                ctx.translate(TIME_SLICE_START_X-self.time_range.get_start_pixel(), 5)
                ctx.translate(time_stamp*self.time_range.pixel_per_second, 0)


                #if self.time_range.pixel_per_second*time_label.step>70:
                #    time_stamp_text = "{0:.02f}".format(time_stamp)
                #    draw_text(ctx, time_stamp_text, 5, 0, text_color="000000", font_name="8")

                draw_straight_line(ctx, 0, time_label.level*TIME_STAMP_LABEL_HEIGHT/len(time_labels),
                    0, TIME_STAMP_LABEL_HEIGHT-5)
                draw_stroke(ctx, 1, EDITOR_LINE_COLOR)
                ctx.restore()
                time_stamp += time_label.step


        if self.time_line:
            time_markers = self.time_line.time_markers
            for label_at in sorted(time_markers.keys()):
                if label_at<visible_time_start:
                    continue
                if label_at>visible_time_end:
                    break
                ctx.save()
                ctx.translate(TIME_SLICE_START_X-self.time_range.get_start_pixel(), 2)
                ctx.translate(label_at*self.time_range.pixel_per_second, 0)

                if self.time_range.pixel_per_second*time_label.step>70 or True:
                    time_stamp_text = time_markers[label_at].text
                    draw_text(ctx, time_stamp_text, 1, 0, text_color="000000", font_name="8",
                        border_color="000000", back_color="ffffff", corner=2, padding=2)

                draw_straight_line(ctx, 0, 0, 0, self.mouse_position_box.height)
                draw_stroke(ctx, 1, EDITOR_LINE_COLOR)
                ctx.restore()

        #draw line under entire time label space
        draw_straight_line(ctx, 0, TIME_STAMP_LABEL_HEIGHT,widget_width, TIME_STAMP_LABEL_HEIGHT)
        draw_stroke(ctx, 1, EDITOR_LINE_COLOR)
        #draw line above entire time label space
        draw_straight_line(ctx, 0, 0,widget_width, 0)
        draw_stroke(ctx, 1, EDITOR_LINE_COLOR)
        ctx.restore()

        if self.time_line:
            for marker_at in sorted(self.time_line.time_markers.keys()):
                time_marker_box = self.time_marker_boxes[marker_at]
                if marker_at<visible_time_start:
                    continue
                if  marker_at>visible_time_end:
                    break
                time_marker_box.draw(ctx)

        if self.mouse_position_box.left>=0:
            #draw current mouse position time label
            ctx.save()
            ctx.translate(TIME_SLICE_START_X , TIME_STAMP_LABEL_HEIGHT)
            ctx.translate(self.mouse_position_box.left+3, 2.5)
            draw_text(ctx, "{0:.3f}".format(self.mouse_time_position), x=0, y=0, padding=3,
                           font_name="8", border_color="2266ff", back_color="ffffff")
            ctx.restore()

            #draw current mouse position line
            ctx.save()
            ctx.translate(TIME_SLICE_START_X, TIME_STAMP_LABEL_HEIGHT)
            self.mouse_position_box.draw(ctx)
            ctx.restore()

        #draw playhead
        if active and len(self.time_line.shape_time_lines) > 0 and \
            self.play_head_box.get_center_x()>=TIME_SLICE_START_X:
            self.play_head_box.draw(ctx)

    def on_drawing_area_mouse_press(self, widget, event):
        if event.button == 1:#Left mouse
            if event.type == Gdk.EventType._2BUTTON_PRESS:#double button click
                if  self.selected_time_slice_box:
                    self.selected_time_slice_box.highlighted = False
                if self.select_time_slice_box_at(self.mouse_point):
                    return
                if self.time_line:
                    error_span = self.time_range.get_seconds_per_pixel()*TIME_MARKER_HIT_MULT
                    closest_time_marker = self.time_line.get_closest_time_marker(
                            at=self.mouse_time_position, error_span=error_span)
                    if closest_time_marker is None:
                        time_marker = self.time_line.add_time_marker(
                            at=self.mouse_time_position,
                            error_span=error_span)
                        if time_marker:
                            self.time_marker_boxes[time_marker.at]=TimeMarkerBox(time_marker)
                        self.update_time_marker_boxes()
                    else:
                        dialog_title = "Edit Marker At{0:.02f}".format(closest_time_marker.at)
                        old_at = closest_time_marker.at
                        dialog = TimeMarkerEditDialog(
                                self.parent_window, dialog_title, closest_time_marker)
                        response = dialog.run()
                        if response == TimeMarkerEditDialog.MARKER_SAVED:
                            self.move_time_marker(closest_time_marker, old_at, closest_time_marker.at)
                            self.update_time_marker_boxes()
                        elif response == TimeMarkerEditDialog.DELETE_MARKER:
                            dialog.destroy()
                            dialog = YesNoDialog(self.parent_window,
                                    "Delete Marker at {0}".format(closest_time_marker.get_formatted_at()),
                                    "Do you really want to delete marker at {0} with label {1}".format(
                                    closest_time_marker.get_formatted_at(), closest_time_marker.text)
                            )
                            if dialog.run() == Gtk.ResponseType.YES:
                                self.delete_time_marker(closest_time_marker)
                                self.update_time_marker_boxes()
                        dialog.destroy()
                        self.select_item_at(self.mouse_point)
                    self.on_drawing_area_mouse_release(widget, event)
                    return

            self.mouse_init_point.x = self.mouse_point.x
            self.mouse_init_point.y = self.mouse_point.y
            self.mouse_pressed = True
            self.init_selected_item = Box()
            self.select_item_at(self.mouse_point)
            self.redraw()

    def on_drawing_area_mouse_release(self, widget, event):
        self.end_movement()
        self.mouse_pressed = False

    def on_drawing_area_mouse_move(self, widget, event):
        self.mouse_point.x = event.x
        self.mouse_point.y = event.y

        self.mouse_point.translate(-DRAW_AREA_PADDING, -TIME_STAMP_LABEL_HEIGHT)
        self.mouse_position_box.left = self.mouse_point.x - TIME_SLICE_START_X
        self.mouse_time_position = self.time_range.get_time_for_extra_x(self.mouse_position_box.left)
        if self.mouse_pressed:
            self.move_active_item(self.mouse_init_point, self.mouse_point)
            if self.selected_time_slice_box:
                self.on_time_slice_box_select()
        self.queue_draw()

    def on_drawing_area_scrollbar_value_changed(self, widget, scroll_dir):
        if not self.time_line: return
        if scroll_dir == "horiz":
            self.time_scroll_to(widget.get_value())
            self.move_play_head_to_time(None)
        elif scroll_dir == "vert":
            value = widget.get_value()
            self.drawing_area_vetical_scroll_to(value)
        self.redraw()

    def drawing_area_vetical_scroll_to(self, value):
        if not self.drawing_area or not self.multi_shape_time_line_box: return
        excess_height = self.multi_shape_time_line_box.height-self.drawing_area.get_allocated_height()
        self.multi_shape_time_line_box.top = -excess_height*value

    def on_configure_event(self, widget, event):
        w = self.drawing_area.get_allocated_width()
        h = self.drawing_area.get_allocated_height()
        self.time_range.set_visible_duration_pixel(w-TIME_SLICE_START_X)
        self.update()

    def on_drawing_area_mouse_scroll(self, widget, event):
        if self.keyboard_object.control_key_pressed:
            if event.direction == Gdk.ScrollDirection.UP:
                zoom = 1.
            elif event.direction == Gdk.ScrollDirection.DOWN:
                zoom = -1.
            if self.keyboard_object.shift_key_pressed:
                self.zoom_vertical(zoom*.1, self.mouse_point)
            else:
                self.zoom_time(zoom*.1)
            self.update_slices_left()
            self.update_drawing_area_scrollbars()
            self.update()
        else:
            if event.direction == Gdk.ScrollDirection.UP:
                value = 1
            elif event.direction == Gdk.ScrollDirection.DOWN:
                value = -1.
            if not self.keyboard_object.shift_key_pressed:
                value = -self.drawing_area_vadjust.get_step_increment()*value
                value += self.drawing_area_vadjust.get_value()
                self.drawing_area_vadjust.set_value(value)
                self.drawing_area_vetical_scroll_to(value)
                self.update()
            else:
                value = self.drawing_area_hadjust.get_step_increment()*value
                value += self.drawing_area_hadjust.get_value()
                self.drawing_area_hadjust.set_value(value)
                self.time_range.scroll_to(value)

        self.move_play_head_to_time(None)
        self.redraw()
