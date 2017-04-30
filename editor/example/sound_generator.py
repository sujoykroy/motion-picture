from gi.repository import Gtk, Gdk
from MotionPicture.gui_utils import *
from MotionPicture.commons import *
from MotionPicture.audio_tools import *
import numpy, scipy, os, parser
from scipy import interpolate
from moviepy.audio.AudioClip import AudioArrayClip
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import dump as XmlDump
from xml.etree.ElementTree import ElementTree as XmlTree
from xml.etree.ElementTree import Element as XmlElement


import numpy as np


class PianoKey(object):
    KEYS = OrderedDict()
    KEY_SINGLE_NAMES = "C C# D D# E F F# G G# A A# B".split(" ")

    def __init__(self, index):
        self.index = index
        self.name = self.get_key_name(index)
        self.frequency = self.get_key_frequency(index)

    @classmethod
    def get_key(cls, name):
        if PianoKey.KEYS.key_exists(name):
            return PianoKey.KEYS[name]
        return None

    @classmethod
    def get_key_name(cls, index):
        if index == 0:
            return "A0"
        if index == 1:
            return "B0"
        key_index = index%12
        scale = ((index-key_index)/12) +1
        return "{0}{1}".format(cls.KEY_SINGLE_NAMES[key_index], scale)

    @classmethod
    def get_key_frequency(cls, index):
        return 2**((index-49)/12.)*440

    @classmethod
    def build_keys(cls):
        PianoKey.KEYS.clear()
        for i in range(88):
            key = cls(i+1)
            PianoKey.KEYS.add(key.name, key)

PianoKey.build_keys()

class InterpolatorContainer(object):
    def __init__(self, doc):
        self.doc = doc

    def __getattr__(self, name):
        return self.doc.interpolators[name]

class Document(object):
    def __init__(self, filename=None):
        self.polygons = dict()
        self.filename = filename
        self.load()
        self.interpolators = dict()
        self.build_interpolators()

    def new_polygon(self, name=None):
        i = 2
        if not name:
            name = "p"
        orig_name = name
        while name in self.polygons:
            name = orig_name + "{0}".format(i)
            i += 2
        polygon = Polygon(points=[Point(0,0), Point(1,0)])
        self.polygons[name] = polygon
        return name

    def get_polygon(self, name):
        if name in self.polygons:
            return self.polygons[name]
        return None

    def get_polygon_names(self):
        return sorted(self.polygons.keys())

    def rename_polygon(self, old_name, new_name):
        polygon = self.polygon(old_name)
        if not polygon:
            return
        if not new_name in self.polygons:
            self.polygons[new_name] = polygon
            del self.polygons[old_name]

    def load(self):
        try:
            tree = ET.parse(self.filename)
        except IOError as e:
            return
        except ET.ParseError as e:
            return
        root = tree.getroot()
        doc = root.find("doc")
        for polygon_elem in doc.findall(Polygon.TAG_NAME):
            polygon = Polygon.create_from_xml_element(polygon_elem)
            polygon_name = polygon_elem.attrib["name"]
            self.polygons[polygon_name] = polygon

    def save(self, filename=None):
        if filename is None:
            filename = self.filename
        root = XmlElement("root")

        doc = XmlElement("doc")
        root.append(doc)

        for polygon_name, polygon in self.polygons.items():
            polygon_elm = polygon.get_xml_element()
            polygon_elm.attrib["name"] = polygon_name
            doc.append(polygon_elm)

        tree = XmlTree(root)
        backup_file = None
        if filename is not None:
            if os.path.isfile(filename):
                backup_file = filename + ".bk"
                os.rename(filename, backup_file)
        try:
            tree.write(filename)
        except TypeError as e:
            if backup_file:
                os.rename(backup_file, filename)
                backup_file = None
        if backup_file:
            os.remove(backup_file)

    def build_interpolators(self):
        for polygon_name, polygon in self.polygons.items():
            self.interpolators[polygon_name] = get_interpolator_for_polygon(polygon)

class DocFormula(object):
    def __init__(self, doc, formula):
        self.doc_inpt = InterpolatorContainer(doc)
        self.formula = formula

    def get_value_at(self, t):
        return self.formula(self.doc_inpt, t)

class Interpolator(object):
    def __init__(self, xs, ys):
        self.formula = interpolate.PchipInterpolator(numpy.array(xs), numpy.array(ys))

    def get_value_at(self, t):
        t %= 1
        return self.formula(t)

    def __call__(self, t):
        return self.get_value_at(t)

def get_interpolator_for_polygon(polygon):
    xs = []
    ys = []
    for point in sorted(polygon.points, key=lambda p: p.x):
        xs.append(point.x)
        ys.append(point.y)
    return Interpolator(xs, ys)

class CurveSamples(object):
    def __init__(self):
        self.xmin =  0.
        self.xmax =  1.
        self.ymin = -1.
        self.ymax = 1.

        self.formulas = None

    def get_x_min_max(self):
        return [self.xmin, self.xmax]

    def get_y_min_max(self):
        return [self.ymin, self.ymax]

    def get_y_base(self):
        return 0.0

    def get_segment_count(self):
        if not self.formulas:
            return 1
        return len(self.formulas)

    def get_sample_at_x(self, segment_index, x):
        if not self.formulas:
            return None
        formula = self.formulas[segment_index]
        return formula.get_value_at(x)

    def get_audio_samples(self, sample_rate, time_period, cycles):
        if len(self.formulas)==0:
            return None

        period_sample_count = sample_rate*time_period
        step_duration = 1.0/period_sample_count
        step_values = numpy.arange(0, 1, step_duration)

        total_samples = None
        for si in range(len(self.formulas)):
            formula = self.formulas[si]
            samples = formula.get_value_at(step_values)

            for i in range(cycles):
                samples = numpy.concatenate((samples, samples[:len(step_values)]))

            if total_samples is None:
                total_samples = samples
            else:
                total_samples = numpy.stack((total_samples, samples), axis=0)
            samples = None
        if len(total_samples.shape)==1:
            total_samples = numpy.stack((total_samples, total_samples))
        return total_samples

    def build_formulas_from_text(self, text, doc):
        self.formulas = eval(parser.expr(text).compile())
        for i in range(len(self.formulas)):
            self.formulas[i] = DocFormula(doc, self.formulas[i])

    def build_formulas_from_polygons(self, polygons):
        self.formulas = []
        for pi in range(len(polygons)):
            polygon = polygons[pi]
            poly = get_interpolator_for_polygon(polygon)
            self.formulas.append(poly)

class SoundCurveViewer(ArrayViewer):
    def __init__(self, keyboard, on_play_callback=None):
        super(SoundCurveViewer, self).__init__(keyboard)
        self.on_play_callback = on_play_callback
        self.polygons = []
        self.audio_player = None
        self.selected_point = None

        self.move_control_box.remove(self.move_backward_button)
        self.move_control_box.remove(self.move_backward_button)
        self.move_control_box.remove(self.threshold_entry)
        self.move_control_box.remove(self.yvalue_apply_button)
        self.move_control_box.remove(self.threshold_entry)
        self.move_control_box.remove(self.threshold_label)
        self.move_control_box.remove(self.multiply_label)
        self.move_control_box.remove(self.threshold_entry)
        self.move_control_box.remove(self.exact_selection_button)
        self.move_control_box.remove(self.exact_selection_entry)

        self.play_start_curve_button = Gtk.Button("Play")
        self.play_start_curve_button.connect("clicked", self.play_curve_button_clicked, "start")
        self.play_stop_curve_button = Gtk.Button("Stop")
        self.play_stop_curve_button.connect("clicked", self.play_curve_button_clicked, "stop")
        self.piano_key_combo_box = NameValueComboBox()
        self.piano_key_combo_box.build_and_set_model(PianoKey.KEYS.keys)
        self.piano_key_combo_box.set_value("C4")
        self.segment_cycle_entry = Gtk.Entry()
        self.segment_cycle_entry.set_text("10")
        self.segment_duration_entry = Gtk.Entry()
        self.segment_duration_entry.set_text("0")

        self.move_control_box.pack_start(
                self.piano_key_combo_box, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_start(
                self.segment_cycle_entry, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_start(
                Gtk.Label("Cycles"), expand=False,  fill=False, padding=0)
        self.move_control_box.pack_start(
                self.segment_duration_entry, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_start(
                Gtk.Label("Seconds"), expand=False,  fill=False, padding=0)
        self.move_control_box.pack_start(
                self.play_start_curve_button, expand=False,  fill=False, padding=0)
        self.move_control_box.pack_start(
                self.play_stop_curve_button, expand=False,  fill=False, padding=0)

        self.curve_audio_raw_segment = None
        self.sample_stroke_width = 5

    def set_samples(self, samples):
        super(SoundCurveViewer, self).set_samples(samples)

    def set_polygons(self, *polygons):
        del self.polygons[:]
        self.polygons.extend(polygons)
        self.samples.build_formulas_from_polygons(polygons)

    def play_curve_button_clicked(self, widget, mode):
        if self.curve_audio_raw_segment:
            self.audio_player.remove_segment(self.curve_audio_raw_segment)
            self.curve_audio_raw_segment = None
        self.audio_player.clear_queue()
        if mode == "start":
            if self.polygons:
                self.samples.build_formulas_from_polygons(self.polygons)
            cycles = int(Text.parse_number(self.segment_cycle_entry.get_text()))
            period = Text.parse_number(self.segment_duration_entry.get_text())
            piano_key = PianoKey.get_key(name=self.piano_key_combo_box.get_value())
            if period <=0:
                period = 1./piano_key.frequency
            samples = self.samples.get_audio_samples(
                self.audio_player.sample_rate, period, cycles)
            if samples is None:
                return
            self.curve_audio_raw_segment = AudioRawSamples(samples, self.audio_player.sample_rate)
            if self.on_play_callback:
                self.on_play_callback()
            self.audio_player.add_segment(self.curve_audio_raw_segment)
            self.play_stop_curve_button.show()
            self.play_start_curve_button.hide()
        else:
            self.play_start_curve_button.show()
            self.play_stop_curve_button.hide()

    def on_drawing_area_draw(self, widget, ctx):
        super(SoundCurveViewer, self).on_drawing_area_draw(widget, ctx)
        if self.samples is None or not self.polygons:
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
        self.rebuild_formulas()

    def rebuild_formulas(self):
        if self.polygons:
            self.samples.build_formulas_from_polygons(self.polygons)
        self.redraw()

    def delete_selected_point(self):
        if self.selected_point:
            pi, point = self.selected_point
            self.polygons[pi].remove_point(point)
            self.selected_point = None
            self.rebuild_formulas()

    def on_drawing_area_mouse_move(self, widget, event):
        self.mouse_point.copy_from(event)
        if self.mouse_pressed and self.selected_point:
            pi, point = self.selected_point
            si, ms_point = self.screen2graph(self.mouse_point)
            if pi != si:
                return
            point.copy_from(ms_point)
            if self.polygons:
                self.samples.build_formulas_from_polygons(self.polygons)
            self.redraw()
        else:
            super(SoundCurveViewer, self).on_drawing_area_mouse_move(widget, event)

class SoundGeneratorEditor(Gtk.Window):
    def __init__(self, filename=None, quit_callback=None, width=200, height=200):
        Gtk.Window.__init__(self)
        self.doc = Document(filename)
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

        self.polygon_control_box = Gtk.HBox()
        self.root_box.pack_start(self.polygon_control_box, expand=False,  fill=False, padding=0)

        self.polygon_names_combo_box = NameValueComboBox()
        self.polygon_names_combo_box.build_and_set_model(self.doc.get_polygon_names())

        self.polygon_names_combo_box.connect("changed", self.polygon_names_combo_box_changed)
        self.create_new_curve_button = Gtk.Button("New Curve")
        self.create_new_curve_button.connect("clicked", self.create_new_curve_button_clicked)

        self.polygon_control_box.pack_start(
                self.polygon_names_combo_box, expand=False,  fill=False, padding=0)
        self.polygon_control_box.pack_start(
                self.create_new_curve_button, expand=False,  fill=False, padding=0)

        self.mix_viewer = SoundCurveViewer(self.keyboard, self.on_mix_viewer_play_started)
        self.mix_viewer.set_samples(CurveSamples())
        self.mix_viewer.sample_stroke_width = 1
        self.root_box.pack_start(
            self.mix_viewer.get_container_box(), expand=True,  fill=True, padding=0)

        self.mix_control_box = Gtk.HBox()
        self.root_box.pack_start(self.mix_control_box, expand=False,  fill=False, padding=0)

        self.load_formula_button = Gtk.Button("Reload Formula")
        self.load_formula_button.connect("clicked", self.load_formula_button_clicked)

        self.mix_control_box.pack_start(
                self.load_formula_button, expand=False,  fill=False, padding=0)

        self.samples_viewer = ArrayViewer(self.keyboard)
        self.root_box.pack_start(
            self.samples_viewer.get_container_box(), expand=True,  fill=True, padding=0)

        self.curve_audio_raw_segment = None
        self.show_all()

        self.audio_player = AudioPlayer(10)
        self.audio_player.start()

        self.curve_viewer.audio_player = self.audio_player
        self.mix_viewer.audio_player = self.audio_player

    def load_formula_button_clicked(self, widget):
        formula_filename = os.path.join(os.path.dirname(__file__), "formula_sample.py")
        formula_file = open(formula_filename, "r")
        formula_text = formula_file.read()
        formula_file.close()
        self.doc.build_interpolators()
        self.mix_viewer.samples.build_formulas_from_text(formula_text, self.doc)
        self.mix_viewer.redraw()

    def polygon_names_combo_box_changed(self, widget):
        polygon_name = widget.get_value()
        self.curve_viewer.set_polygons(self.doc.get_polygon(polygon_name))
        self.curve_viewer.redraw()

    def create_new_curve_button_clicked(self, widget):
        polygon_name = self.doc.new_polygon()
        self.polygon_names_combo_box.build_and_set_model(self.doc.get_polygon_names())
        self.polygon_names_combo_box.set_value(polygon_name)

    def on_mix_viewer_play_started(self):
        audio_segment = self.mix_viewer.curve_audio_raw_segment
        self.samples_viewer.set_samples(audio_segment)
        self.samples_viewer.redraw()

        if False:
            clip = AudioArrayClip(audio_segment.samples.T, fps=audio_segment.sample_rate)
            clip.write_audiofile("/home/sujoy/Temporary/mix_viewer.wav")

    def on_drawing_area_key_press(self, widget, event):
        self.keyboard.set_keypress(event.keyval, pressed=True)

    def on_drawing_area_key_release(self, widget, event):
        self.keyboard.set_keypress(event.keyval, pressed=False)
        if event.string == "s":
            self.doc.save()
        if event.string == "x":
            self.curve_viewer.delete_selected_point()

    def quit(self, widget, event):
        if self.audio_player:
            self.audio_player.close()
            self.audio_player = None
        if self.quit_callback:
            self.quit_callback()


def on_quit():
    Gtk.main_quit()
    AudioJack.get_thread().close()

sound_gn_editor = SoundGeneratorEditor(quit_callback=on_quit,
        filename="/home/sujoy/Temporary/sd.xml")


Gtk.main()
