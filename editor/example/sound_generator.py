from gi.repository import Gtk, Gdk
from MotionPicture.gui_utils import *
from MotionPicture.commons import *
from MotionPicture.audio_tools import *
import numpy, scipy
from scipy import interpolate

class CurveSamples(object):
    def __init__(self):
        self.xmin =  0.
        self.xmax =  1.
        self.ymin = -5.
        self.ymax = 5.

        self.poly = None

    def set_curves(self, curves):
        self.curves = curves

    def get_x_min_max(self):
        return [self.xmin, self.xmax]

    def get_y_min_max(self):
        return [self.ymin, self.ymax]

    def get_y_base(self):
        return 0.0

    def get_segment_count(self):
        return 1

    def get_sample_at_x(self, segment_index, x):
        #return 0
        if self.poly is None:
            return 0
        return self.poly[segment_index](x)

    def get_audio_samples(self, sample_rate, frequency, duration):
        period_sample_count = sample_rate*1.0/frequency
        step_duration = 1.0/period_sample_count
        step_values = numpy.arange(0, 1., step_duration)
        samples = self.poly[0](step_values)
        if len(samples.shape)==0:
            return None
        period_count = duration*1.0/frequency
        lower_rounded_period_count = int(math.floor(period_count))
        for i in range(lower_rounded_period_count):
            samples = numpy.concatenate((samples, samples[:len(step_values)]))
        if lower_rounded_period_count<period_count:
            upper_bound = len(step_values)*(period_count-lower_rounded_period_count)
            samples = numpy.concatenate((samples, samples[:int(upper_bound)]))
        return numpy.stack((samples, samples))

    def build_poly(self, polygons):
        self.poly = []
        for pi in range(len(polygons)):
            xs = []
            ys = []
            polygon = polygons[pi]
            for point in sorted(polygon.points, key=lambda p: p.x):
                xs.append(point.x)
                ys.append(point.y)
            poly = interpolate.PchipInterpolator(numpy.array(xs), numpy.array(ys))
            self.poly.append(poly)

class SoundCurveViewer(ArrayViewer):
    def __init__(self, keyboard):
        super(SoundCurveViewer, self).__init__(keyboard)
        self.polygons = []
        self.selected_point = None

    def set_samples(self, samples):
        super(SoundCurveViewer, self).set_samples(samples)
        xmin, xmax = self.samples.get_x_min_max()
        xdiff = xmax - xmin
        ybase = self.samples.get_y_base()
        start_point = Point(xmin, ybase)
        end_point = Point(xmax, ybase)
        for si in range(samples.get_segment_count()):
            self.polygons.append(Polygon(points=[start_point.copy(), end_point.copy()]))

    def on_drawing_area_draw(self, widget, ctx):
        super(SoundCurveViewer, self).on_drawing_area_draw(widget, ctx)
        if self.samples is None:
            return

        widget_width = widget.get_allocated_width()
        widget_height = widget.get_allocated_height()

        y_segment_count = self.samples.get_segment_count()
        for segment_index in range(y_segment_count):
            polygon = self.polygons[segment_index]
            for point in polygon.points:
                point = self.graph2screen(segment_index, point)
                ctx.new_path()
                ctx.save()
                ctx.translate(point.x, point.y)
                ctx.scale(10, 10)
                ctx.move_to(.5,0)
                ctx.arc(0,0,.5,0, 2*math.pi)
                ctx.close_path()
                ctx.restore()

                draw_stroke(ctx, 2, "0000FF")

    def on_drawing_area_mouse_press(self, widget, event):
        self.mouse_pressed = True
        self.selected_point = None

        if self.samples is None:
            return
        if event.button == 1:#Left mouse
            si, graph_point = self.screen2graph(self.mouse_point)
            added = False
            if event.type == Gdk.EventType._2BUTTON_PRESS:#double button click
                self.polygons[si].add_point(graph_point)
                added = True
            if not added:
                for pi in range(len(self.polygons)):
                    polygon = self.polygons[pi]
                    for point in polygon.points:
                        screen_point = self.graph2screen(pi, point)
                        if self.mouse_point.distance(screen_point)<10:
                            self.selected_point=(pi, point)
                            break
            if self.selected_point is None:
                self.selection = [graph_point.x, graph_point.x]
            self.redraw()

    def on_drawing_area_mouse_release(self, widget, event):
        self.mouse_pressed = False
        self.selected_point = None
        if self.selection:
            if self.selection[0] == self.selection[1]:
                self.selection = None

    def on_drawing_area_mouse_move(self, widget, event):
        self.mouse_point.copy_from(event)
        if self.mouse_pressed and self.selected_point:
            pi, point = self.selected_point
            si, ms_point = self.screen2graph(self.mouse_point)
            if pi != si:
                return
            point.copy_from(ms_point)
            self.samples.build_poly(self.polygons)
            self.redraw()
        else:
            super(SoundCurveViewer, self).on_drawing_area_mouse_move(widget, event)

class SoundGeneratorEditor(Gtk.Window):
    def __init__(self, filename=None, quit_callback=None, width=200, height=200):
        Gtk.Window.__init__(self)
        self.quit_callback = quit_callback
        self.keyboard = Keyboard()

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(width, height)
        self.connect("delete-event", self.quit)
        self.connect("key-press-event", self.on_drawing_area_key_press)
        self.connect("key-release-event", self.on_drawing_area_key_release)

        self.topmost_box = Gtk.HBox()
        self.add(self.topmost_box)

        self.root_box = Gtk.VBox()
        self.topmost_box.pack_start(self.root_box, expand=True,  fill=True, padding=0)

        self.curve_viewer = SoundCurveViewer(self.keyboard)
        self.curve_viewer.set_samples(CurveSamples())
        self.root_box.pack_start(
            self.curve_viewer.get_container_box(), expand=True,  fill=True, padding=0)

        self.play_control_box = Gtk.HBox()
        self.root_box.pack_start(self.play_control_box, expand=False,  fill=False, padding=0)

        self.play_start_curve_button = Gtk.Button("Play")
        self.play_start_curve_button.connect("clicked", self.play_curve_button_clicked, "start")
        self.play_stop_curve_button = Gtk.Button("Stop")
        self.play_stop_curve_button.connect("clicked", self.play_curve_button_clicked, "stop")

        self.play_control_box.pack_start(
                self.play_start_curve_button, expand=False,  fill=False, padding=0)
        self.play_control_box.pack_start(
                self.play_stop_curve_button, expand=False,  fill=False, padding=0)

        self.audio_player = None
        self.curve_audio_raw_segment = None
        self.show_all()

    def play_curve_button_clicked(self, widget, mode):
        if self.curve_audio_raw_segment:
            self.audio_player.remove_segment(self.curve_audio_raw_segment)
            self.curve_audio_raw_segment = None
        if not self.audio_player:
            self.audio_player = AudioPlayer(10)
            self.audio_player.start()
        self.audio_player.clear_queue()
        if mode == "start":
            self.curve_viewer.samples.build_poly(self.curve_viewer.polygons)
            samples = self.curve_viewer.samples.get_audio_samples(
                self.audio_player.sample_rate, 440, 10)
            print samples.shape
            if samples is None:
                print "problem"
                return
            self.curve_audio_raw_segment = AudioRawSamples(samples, self.audio_player.sample_rate)

            self.audio_player.add_segment(self.curve_audio_raw_segment)
            self.play_stop_curve_button.show()
            self.play_start_curve_button.hide()
        else:
            self.play_start_curve_button.show()
            self.play_stop_curve_button.hide()

    def on_drawing_area_key_press(self, widget, event):
        self.keyboard.set_keypress(event.keyval, pressed=True)

    def on_drawing_area_key_release(self, widget, event):
        self.keyboard.set_keypress(event.keyval, pressed=False)

    def quit(self, widget, event):
        if self.audio_player:
            self.audio_player.close()
            self.audio_player = None
        if self.quit_callback:
            self.quit_callback()

def on_quit():
    Gtk.main_quit()
    AudioJack.get_thread().close()

sound_gn_editor = SoundGeneratorEditor(quit_callback=on_quit)
Gtk.main()
