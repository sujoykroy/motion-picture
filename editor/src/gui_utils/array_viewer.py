import numpy
import cairo
from gi.repository import Gdk
from ..commons import *
import cairo

class ArrayViewer(object):
    def __init__(self, keyboard):
        self. keyboard = keyboard

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_events(
            Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK|\
            Gdk.EventMask.BUTTON_RELEASE_MASK|Gdk.EventMask.SCROLL_MASK)
        self.drawing_area.connect("draw", self.on_drawing_area_draw)
        self.drawing_area.connect("button-press-event", self.on_drawing_area_mouse_press)
        self.drawing_area.connect("button-release-event", self.on_drawing_area_mouse_release)
        self.drawing_area.connect("motion-notify-event", self.on_drawing_area_mouse_move)
        self.drawing_area.connect("scroll-event", self.on_drawing_area_mouse_scroll)

        self.drawing_area_vadjust = Gtk.Adjustment(0, 0, 1., .1, 0, 0)
        self.drawing_area_vscrollbar = Gtk.VScrollbar(self.drawing_area_vadjust)
        self.drawing_area_vscrollbar.connect("value-changed",
                            self.on_drawing_area_scrollbar_value_changed, "vert")

        self.drawing_area_hadjust = Gtk.Adjustment(0, 0, 1., .0001, 0, 0)
        self.drawing_area_hscrollbar = Gtk.HScrollbar(self.drawing_area_hadjust)
        self.drawing_area_hscrollbar.connect("value-changed",
                            self.on_drawing_area_scrollbar_value_changed, "horiz")

        self.drawing_area_container_vbox = Gtk.VBox()

        self.drawing_area_container_hbox = Gtk.HBox()
        self.drawing_area_container_vbox.pack_start(
            self.drawing_area_container_hbox, expand=True,  fill=True, padding=0)
        self.drawing_area_container_vbox.pack_start(
            self.drawing_area_hscrollbar, expand=False,  fill=True, padding=0)

        self.drawing_area_container_hbox.pack_start(
            self.drawing_area, expand=True,  fill=True, padding=0)
        self.drawing_area_container_hbox.pack_start(
            self.drawing_area_vscrollbar, expand=False,  fill=True, padding=0)


        self.move_control_box = Gtk.HBox()
        self.drawing_area_container_vbox.pack_start(
            self.move_control_box, expand=False,  fill=False, padding=0)
        self.move_forward_button = Gtk.Button(">")
        self.move_forward_button.connect("clicked", self.move_button_clicked, "forward")
        self.move_backward_button = Gtk.Button("<")
        self.move_backward_button.connect("clicked", self.move_button_clicked, "backward")

        self.reset_dimension_button = Gtk.Button("Reset")
        self.reset_dimension_button.connect("clicked", self.reset_dimension_button_clicked)

        self.yvalue_adjust_button = Gtk.SpinButton.new_with_range(0, 100, .1)
        self.yvalue_adjust_button.set_digits(3)
        self.yvalue_adjust_button.set_numeric(True)

        self.yvalue_apply_button = Gtk.Button("Apply")
        self.yvalue_apply_button.connect("clicked", self.yvalue_apply_button_clicked)

        self.exact_selection_entry = Gtk.Entry()
        self.exact_selection_button = Gtk.Button("Exact Selection")
        self.exact_selection_button.connect("clicked", self.exact_selection_button_clicked)

        self.threshold_entry = Gtk.Entry()
        self.threshold_entry.set_text("<|Value|")

        self.position_checkbutton = Gtk.CheckButton("")
        self.position_entry = Gtk.Entry()
        self.position_entry.set_editable(False)

        self.move_control_box.pack_start(self.position_checkbutton, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_start(self.position_entry, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_end(self.reset_dimension_button, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_end(self.move_forward_button, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_end(self.move_backward_button, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_end(self.yvalue_apply_button, expand=False,  fill=False, padding=5)
        self.move_control_box.pack_end(self.threshold_entry, expand=False,  fill=False, padding=0)
        self.threshold_label = Gtk.Label("Threhsold")
        self.move_control_box.pack_end(self.threshold_label, expand=False,  fill=False, padding=5)
        self.move_control_box.pack_end(self.yvalue_adjust_button, expand=False,  fill=False, padding=0)
        self.multiply_label = Gtk.Label("Multiply")
        self.move_control_box.pack_end(self.multiply_label, expand=False,  fill=False, padding=5)

        self.move_control_box.pack_end(self.exact_selection_button, expand=False,  fill=False, padding=5)
        self.move_control_box.pack_end(self.exact_selection_entry, expand=False,  fill=False, padding=0)

        self.samples = None
        self.selection = None
        self.mouse_point = Point(0, 0)
        self.mouse_pressed = False
        self.graph_colors = [Color.parse("da2daf"), Color.parse("FF0000")]
        self.reset_dimensions()
        self.playhead = None
        self.canvas = None
        self.selection_width = None
        self.sample_stroke_width = 1

    def set_playhead(self, playhead):
        self.playhead = playhead
        self.redraw(clear_cache=False)

    def reset_dimensions(self, redraw=False):
        self.x_shift = 0.0
        self.y_shift = 0.0
        self.x_mult = 1.0
        self.y_mult = 1.0
        if redraw:
            self.redraw()

    def get_container_box(self):
        return self.drawing_area_container_vbox

    def get_selected_samples(self, padded=False):
        if self.selection:
            start_x, end_x = self.selection[:]
            if start_x>end_x:
                start_x, end_x = end_x, start_x
            samples = self.samples.get_samples_in_between(start_x, end_x, padded=padded)
        else:
            samples = self.samples.get_samples_in_between()
        return samples

    def get_selection(self):
        if self.selection:
            selection = self.selection[:]
            if selection[0]>selection[1]:
                selection[0], selection[1] = selection[1], selection[0]
            return selection
        else:
            return self.samples.get_x_min_max()
        return None

    def set_samples(self, samples):
        #self.reset_dimensions()
        self.samples = samples
        self.update_scrollbars()
        self.redraw()

    def set_x_shift(self, x_shift):
        xmin, xmax = self.samples.get_x_min_max()
        if x_shift<xmin:
            x_shift = xmin
        end_shift = (xmax-xmin)*(1-1.0/self.x_mult)
        if x_shift>end_shift:
            x_shift = xmax
        self.x_shift = x_shift

    def set_x_shift_incre(self, x_shift):
        self.set_x_shift(self.x_shift+x_shift)

    def redraw(self, clear_cache=True):
        #if clear_cache:
        #    #self.build_canvas()
        self.drawing_area.queue_draw()

    def exact_selection_button_clicked(self, widget):
        if not self.samples:
            return
        text = self.exact_selection_entry.get_text()
        xmin, xmax = self.samples.get_x_min_max()
        arr = text.split("-")
        start_x = Text.parse_number(arr[0])
        if start_x is None or start_x<xmin:
            start_x = xmin
        end_x = None
        if len(arr)>1:
            end_x = Text.parse_number(arr[1])
        if end_x is None or end_x>xmax:
            end_x = xmax
        self.selection= [start_x, end_x]
        self.exact_selection_entry.set_text("{0}-{1}".format(start_x, end_x))
        self.redraw()

    def move_button_clicked(self, widget, direction):
        if direction == "forward":
            direction = 1.
        else:
            direction = -1.
        x_incre = 10
        x_incre *= self.get_samples_x_spread()*1.0/self.drawing_area.get_allocated_width()
        x_incre /= self.x_mult
        self.set_x_shift_incre(direction*x_incre)
        self.redraw()

    def reset_dimension_button_clicked(self, widget):
        self.reset_dimensions()
        self.update_scrollbars()
        self.redraw()

    def yvalue_apply_button_clicked(self, widget):
        mult = self.yvalue_adjust_button.get_value()
        selection = self.get_selection()
        if not selection:
            selection = self.samples.get_x_min_max()

        thresholds = Threshold.parse(self.threshold_entry.get_text())
        self.samples.apply_y_mult_replace(
            selection[0], selection[1], mult, thresholds)
        self.redraw()

    def pre_draw(self, segment_index, ctx):
        ctx.set_matrix(self.get_matrix(segment_index))
        """
        widget_width = self.drawing_area.get_allocated_width()
        widget_height = self.drawing_area.get_allocated_height()

        xmin, xmax = self.samples.get_x_min_max()
        ymin, ymax = self.samples.get_y_min_max()
        ydiff = ymax-ymin
        segments = self.samples.get_segment_count()

        ctx.scale(float(widget_width)/(xmax-xmin), widget_height)
        ctx.scale(self.x_mult, self.y_mult)
        ctx.translate(-self.x_shift, -self.y_shift)
        #ctx.translate(0, ydiff)
        #ctx.scale(1, -1)
        #ctx.translate(-xmin, -ymin)
        if segment_index>=0:
            ybase = self.samples.get_y_base()
            ctx.scale(1, 1/(ydiff*segments))
            ctx.translate(0, ymax-ybase + segment_index*ydiff)
            ctx.scale(1, -1)
        """

    def on_drawing_area_draw(self, widget, ctx):
        widget_width = widget.get_allocated_width()
        widget_height = widget.get_allocated_height()

        ctx.rectangle(0, 0, widget_width, widget_height)
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill()

        if self.samples is None:
            return

        y_segment_count = self.samples.get_segment_count()
        xmin, xmax = self.samples.get_x_min_max()
        ymin, ymax = self.samples.get_y_min_max()
        xstep = float(xmax-xmin)/(self.x_mult*widget_width)
        ystep = float(ymax-ymin)*y_segment_count/(self.y_mult*widget_height)
        ybase = self.samples.get_y_base()

        if self.selection:
            ctx.save()
            self.pre_draw(-1, ctx)
            ctx.rectangle(self.selection[0], 0, self.selection[1]-self.selection[0], 1)
            draw_fill(ctx, "00FF00")
            ctx.restore()

        if self.playhead is not None:
            ctx.save()
            self.pre_draw(-1, ctx)
            ctx.new_path()
            ph = self.playhead
            ctx.move_to(ph, 0.)
            ctx.line_to(ph, 1.)
            ctx.restore()
            draw_stroke(ctx, 2, "000000")

        for segment_index in range(y_segment_count):
            ctx.save()
            self.pre_draw(segment_index, ctx)
            ctx.new_path()
            ctx.move_to(xmin, ybase)
            ctx.line_to(xmax, ybase)
            ctx.move_to(xmin, ymin)
            ctx.line_to(xmax, ymin)
            ctx.move_to(xmin, ymax)
            ctx.line_to(xmax, ymax)
            ctx.restore()
            draw_stroke(ctx, 1.1, "000000")

            ctx.save()
            self.pre_draw(segment_index, ctx)
            ctx.new_path()
            for pixel in range(widget_width):
                x = self.x_shift+pixel*xstep
                y = self.samples.get_sample_at_x(segment_index, x)
                if y is None:
                    continue
                if pixel == 0:
                    ctx.move_to(x, y)
                else:
                    ctx.line_to(x, y)
            ctx.restore()
            draw_stroke(ctx, self.sample_stroke_width, self.graph_colors[segment_index])

            text_width = 100
            for pixel in range(text_width, widget_width, text_width):
                x = self.x_shift+pixel*xstep
                y = ybase
                ctx.save()
                self.pre_draw(segment_index, ctx)
                ctx.new_path()
                ctx.move_to(x, y+ystep*5)
                ctx.line_to(x, y-ystep*10)
                ctx.restore()
                draw_stroke(ctx, 1, "000000")

                point = self.graph2screen(segment_index, Point(x,y))
                draw_text(ctx, x=point.x+3, y=point.y,
                    height=10, fit_height=True,
                    width=50, fit_width=True,
                    text="{0:.3f}".format(x))

            text_height = 50
            segment_height = widget_height*self.y_mult/y_segment_count
            for pixel in range(0, int(segment_height)-text_height, text_height):
                x = self.x_shift
                y = ymax-pixel*ystep
                ctx.save()
                self.pre_draw(segment_index, ctx)
                ctx.new_path()
                ctx.move_to(x, y)
                ctx.line_to(x+xstep*5, y)
                ctx.restore()
                draw_stroke(ctx, 1, "000000")

                point = self.graph2screen(segment_index, Point(x, y))
                draw_text(ctx, x=0, y=point.y+3,
                    height=text_height, fit_height=True,
                    width=50, fit_width=True,
                    text="{0:.2f}".format(y))

    def on_drawing_area_scrollbar_value_changed(self, widget, scroll_dir):
        self.selected_point = None
        value = widget.get_value()
        if scroll_dir == "horiz":
            xmin, xmax = self.samples.get_x_min_max()
            if self.x_mult>1:
                x_shift = (1.-1./self.x_mult)*(xmax-xmin)*value
                self.set_x_shift(x_shift)
            else:
                self.set_x_shift(xmin)
        elif scroll_dir == "vert":
            if self.y_mult>1:
                self.y_shift = (1-1.0/self.y_mult)*value
            else:
                self.y_shift = 0
        self.redraw()

    def on_drawing_area_mouse_scroll(self, widget, event):
        self.selected_point = None
        if self.keyboard.control_key_pressed:
            old_mouse_screen_point = self.mouse_point.copy()
            old_mouse_graph_point = self.screen2graph(old_mouse_screen_point, all_segments=True)
            if event.direction == Gdk.ScrollDirection.UP:
                zoom = 1.
            elif event.direction == Gdk.ScrollDirection.DOWN:
                zoom = -1.
            if self.keyboard.shift_key_pressed:
                self.y_mult *= (1+.1*zoom)
                if self.y_mult<1:
                    self.y_mult = 1.
            else:
                self.x_mult *=  (1+.1*zoom)
                if self.x_mult<1:
                    self.x_mult = 1.
                self.drawing_area_vadjust.set_step_increment(.1/self.x_mult)
            new_mouse_graph_point = self.screen2graph(old_mouse_screen_point, all_segments=True)
            diff_graph_point = old_mouse_graph_point.diff(new_mouse_graph_point)
            self.set_x_shift_incre(diff_graph_point.x)
            self.y_shift += diff_graph_point.y
            self.update_scrollbars()
            self.redraw()
        else:
            if event.direction == Gdk.ScrollDirection.UP:
                direction = -1.
            elif event.direction == Gdk.ScrollDirection.DOWN:
                direction = 1.
            value = self.drawing_area_vscrollbar.get_value()*(1+.1*direction/self.y_mult)
            self.drawing_area_vscrollbar.set_value(value)
            self.redraw()

    def on_drawing_area_mouse_press(self, widget, event):
        self.mouse_pressed = True
        self.selected_point = None

        if self.samples is None:
            return
        if event.button == 1:#Left mouse
            si, graph_point = self.screen2graph(self.mouse_point)
            self.selection = [graph_point.x, graph_point.x]
            self.redraw()

    def on_drawing_area_mouse_release(self, widget, event):
        self.mouse_pressed = False
        self.selected_point = None
        if self.selection:
            if self.selection[0] == self.selection[1]:
                self.selection = None
            self.yvalue_adjust_button.set_value(1.0)
        if self.selection:
            self.exact_selection_entry.set_text("{0}-{1}".format(*self.selection))

    def on_drawing_area_mouse_move(self, widget, event):
        self.mouse_point.copy_from(event)
        if self.mouse_pressed and self.selection:
            if self.selection_width is not None:
                self.selection[1] = self.selection[0]+self.selection_width
            else:
                self.selection[1]  = self.screen2graph(self.mouse_point, all_segments=True).x
            self.redraw()
        if self.samples and self.position_checkbutton.get_active():
            si, graph_point = self.screen2graph(self.mouse_point)
            self.position_entry.set_text("[{0:.2f}, {1:.2f}]".format(graph_point.x, graph_point.y))

    def update_scrollbars(self):
        if self.y_mult>1:
            v_value = self.y_shift/(1.-1./self.y_mult)
        else:
            v_value = 0.
        self.drawing_area_vscrollbar.set_value(v_value)

        if self.x_mult>1:
            h_value = self.x_shift/((1.-1./self.x_mult)*self.get_samples_x_spread())
        else:
            h_value = 0.
        self.drawing_area_hscrollbar.set_value(h_value)

    def screen2graph(self, point, all_segments=False):
        p = point.copy()
        """
        p.x *= self.get_samples_x_spread()*1.0/self.drawing_area.get_allocated_width()
        p.x /= self.x_mult
        p.x += self.x_shift
        """
        ymin, ymax = self.samples.get_y_min_max()
        ydiff = ymax-ymin

        segment_count = self.samples.get_segment_count()

        p.y *= 1.0/self.drawing_area.get_allocated_height()
        p.y /= self.y_mult
        p.y += self.y_shift

        if not all_segments:
            p.y *= ydiff*segment_count
            ybase = self.samples.get_y_base()

            segment_index = int(math.floor(p.y/ydiff))
            p.y -= segment_index*ydiff
            p.y  = ymax -ybase - p.y
        else:
            segment_index = -1

        #cairo matrix is being used as python's own floating point doesn't match
        #cairo's precision in many cases.
        matrix = self.get_matrix(segment_index)
        matrix.invert()
        p = Point(*matrix.transform_point(point.x, point.y))

        if all_segments:
            return p
        return segment_index, p

    def graph2screen(self, segment_index, point):
        matrix = self.get_matrix(segment_index)
        p = Point(*matrix.transform_point(point.x, point.y))
        return p
        """
        p = point.copy()
        p.x -= self.x_shift
        p.x *= self.x_mult
        p.x *= self.drawing_area.get_allocated_width()*1.0/self.get_samples_x_spread()

        ymin, ymax = self.samples.get_y_min_max()
        ydiff = ymax-ymin
        ybase = self.samples.get_y_base()
        segments = self.samples.get_segment_count()
        p.y = p.y - ybase
        p.y = ymax-p.y
        p.y += segment_index*ydiff
        p.y /= segments*ydiff
        p.y -= self.y_shift
        p.y *= self.y_mult
        p.y *= self.drawing_area.get_allocated_height()
        return p
        """

    def get_matrix(self, segment_index):
        xmin, xmax = self.samples.get_x_min_max()
        ymin, ymax = self.samples.get_y_min_max()
        ydiff = ymax-ymin
        segments = self.samples.get_segment_count()

        matrix = cairo.Matrix()
        widget_height = 1.0*self.drawing_area.get_allocated_height()
        widget_width = 1.0*self.drawing_area.get_allocated_width()
        matrix.scale(float(widget_width)/(xmax-xmin), widget_height)
        matrix.scale(self.x_mult, self.y_mult)
        matrix.translate(-self.x_shift, -self.y_shift)

        if segment_index>=0:
            ybase = self.samples.get_y_base()
            matrix.scale(1, 1/(ydiff*segments))
            matrix.translate(0, ymax-ybase + segment_index*ydiff)
            matrix.scale(1, -1)
        return matrix

    def get_samples_x_spread(self):
        xmin, xmax = self.samples.get_x_min_max()
        return xmax-xmin

    def get_samples_y_spread(self):
        ymin, ymax = self.samples.get_y_min_max()
        return ymax-ymin

    def get_samples_y_max(self):
        ymin, ymax = self.samples.get_y_min_max()
        return ymax
