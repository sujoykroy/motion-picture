from gi.repository import Gtk
from shape_prop_box import ShapePropBox
from  shape_form_prop_box import ShapeFormPropBox
from curve_smooth_prop_box import CurveSmoothPropBox

class PropGrid(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.row_count = 0

    def add(self, item):
        if isinstance(item, ShapePropBox):
            prop_box = item
            r = self.row_count
            for widget_row in prop_box.widget_rows:
                c = 0
                for widget in widget_row:
                    if len(widget_row) == 2 and c == 1:
                        width=4
                    else:
                        width = 1
                    self.attach(widget, left=c, top=r, width=width, height=1)
                    c += 1
                r += 1
            self.row_count = r
        elif isinstance(item, ShapeFormPropBox):
            prop_box = item
            r = self.row_count
            self.attach(prop_box.form_label, left=0, top=r, width=3, height=1)
            self.attach(prop_box.forms_combo_box, left=0, top=r+1, width=3, height=1)
            self.attach(prop_box.form_button_box, left=0, top=r+2, width=3, height=1)
            self.row_count += 3
        elif isinstance(item, CurveSmoothPropBox):
            prop_box = item
            r = self.row_count
            self.attach(prop_box.heading, left=0, top=r, width=3, height=1)
            self.attach(prop_box.spin_button, left=0, top=r+1, width=3, height=1)
            self.attach(prop_box.apply_button, left=0, top=r+2, width=1, height=1)
            self.row_count += 3
        else:
            self.attach(item, left=0, top=self.row_count, width=3, height=1)
            self.row_count += 1

    def add_all(self, *items):
        for item in items:
            self.add(item)

