from gi.repository import Gtk
from ..commons import Curve, BezierPoint

class CurveSmoothPropBox(object):
    def __init__(self, draw_callback, get_shape_manager_callback):
        self.curve_shape = None
        self.draw_callback = draw_callback
        self.get_shape_manager_callback = get_shape_manager_callback

        self.heading = Gtk.Label("Smooth")

        adjustment = Gtk.Adjustment(0, 0, 360, .1, 1, 1)
        self.spin_button = Gtk.SpinButton()
        self.spin_button.set_digits(2)
        self.spin_button.set_numeric(True)
        self.spin_button.set_adjustment(adjustment)

        self.apply_button = Gtk.Button("Apply")
        self.apply_button.connect("clicked", self.apply_button_clicked)

    def hide(self):
        self.heading.hide()
        self.spin_button.hide()
        self.apply_button.hide()

    def show(self):
        self.heading.show()
        self.spin_button.show()
        self.apply_button.show()

    def set_curve_shape(self, curve_shape):
        self.curve_shape = curve_shape

    def apply_button_clicked(self, widget):
        angle = self.spin_button.get_value()

        shape_manager = self.get_shape_manager_callback()
        shape_editor = shape_manager.shape_editor

        if not shape_editor: return
        point_indices = shape_editor.get_selected_moveable_point_indices()
        if not point_indices:
            new_curves = []
            for curve in self.curve_shape.curves:
                curve = curve.copy()
                curve.smooth_out(angle)
                new_curves.append(curve)
        else:
            new_curves = []
            curve_indices = list(sorted(point_indices.keys()))

            for curve_index in curve_indices:
                len_new_curves = len(new_curves)
                for ci in range(len_new_curves, curve_index, 1):
                    new_curves.append(self.curve_shape.curves[ci].copy())

                new_curve = None
                curve_fragment = None
                last_point_index = None

                point_indices = list(sorted(point_indices[curve_index].keys()))
                for i  in range(len(point_indices)):
                    point_index = point_indices[i]
                    if point_index == -1:
                        point = self.curve_shape.curves[curve_index].origin.copy()
                        curve_fragment = Curve(origin=point)
                        last_point_index = point_index
                        continue

                    point = self.curve_shape.curves[curve_index].bezier_points[point_index].copy()

                    if last_point_index is None and point_index>-1:
                        new_curve = Curve(origin=self.curve_shape.curves[curve_index].origin.copy())
                        for pi in range(0, point_index):
                            new_curve.add_bezier_point(
                                self.curve_shape.curves[curve_index].bezier_points[pi].copy())

                    if (last_point_index is not None and (point_index-last_point_index)>1) or \
                        (i>1 and i == len(point_indices)-1):
                        if curve_fragment:
                            if curve_fragment.bezier_points:
                                curve_fragment.smooth_out(angle)
                                if not new_curve:
                                    new_curve = curve_fragment
                                else:
                                    new_curve.bezier_points.extend(curve_fragment.bezier_points)
                            else:
                                if not new_curve:
                                    new_curve = curve_fragment
                            curve_fragment = None

                    if curve_fragment is None:
                        curve_fragment = Curve(origin=point.dest.copy())
                    curve_fragment.add_bezier_point(point)

                    last_point_index = point_index

                if new_curve:
                    for pi in range(point_indices[-1], \
                                    len(self.curve_shape.curves[curve_index].bezier_points)):
                        new_curve.add_bezier_point(
                            self.curve_shape.curves[curve_index].bezier_points[pi].copy())
                    new_curves.append(new_curve)

        task = shape_manager.shape_editor_task_start()
        self.curve_shape.curves = new_curves
        shape_manager.shape_editor_task_end(task)
        self.draw_callback()

