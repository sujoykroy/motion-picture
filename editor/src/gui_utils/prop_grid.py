from gi.repository import Gtk
from shape_prop_box import ShapePropBox
from shape_form_prop_box import ShapeFormPropBox
from curve_smooth_prop_box import CurveSmoothPropBox
from misc_prop_boxes import CustomPropsBox
from point_group_shape_list_box import PointGroupShapeListBox
from interior_pose_box import InteriorPoseBox

class PropGrid(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.row_count = 0
        self.added_items = []
        self.added_sub_items = []
        self.newly_children = []

    def attach(self, child, left, top, width, height):
        super(PropGrid, self).attach(child, left, top, width, height)
        self.newly_children.append(child)

    def add(self, item):
        del self.newly_children[:]

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
                    widget.show_all()
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
        elif isinstance(item, PointGroupShapeListBox):
            prop_box = item
            r = self.row_count
            self.attach(prop_box.label, left=0, top=r, width=1, height=1)
            self.attach(prop_box.shape_list_combo_box, left=1, top=r, width=3, height=1)
            self.row_count += 1
        elif isinstance(item, InteriorPoseBox):
            prop_box = item
            r = self.row_count
            self.attach(prop_box.label, left=0, top=r, width=4, height=1)
            self.attach(prop_box.pose_name_entry, left=0, top=r+1, width=2, height=1)
            self.attach(prop_box.add_button, left=2, top=r+1, width=1, height=1)
            self.row_count += 2
        else:
            self.attach(item, left=0, top=self.row_count, width=4, height=1)
            self.row_count += 1

        self.added_items.append(item)
        self.added_sub_items.append(self.newly_children[:])
        del self.newly_children[:]

    def add_all(self, *items):
        for item in items:
            self.add(item)

    def remove_item(self, item):
        if item in self.added_items:
            index = self.added_items.index(item)
            for sub_item in self.added_sub_items[index]:
                self.remove(sub_item)
            del self.added_items[index]
            del self.added_sub_items[index]

