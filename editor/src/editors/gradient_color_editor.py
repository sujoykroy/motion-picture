from ..commons.draw_utils import draw_stroke
from ..shapes import OvalEditBox
from ..commons import Color, Point
from gi.repository import Gtk, Gdk

class ColorPointBox(OvalEditBox):
    def __init__(self, color_point_index, color_point, pos_frac):
        OvalEditBox.__init__(self,
            color_point.point, fill_color=color_point.color, radius=10, is_percent=False)
        self.border_color = Color(1,1,0,1)
        self.color_point_index = color_point_index
        self.color_point = color_point
        self.pos_frac = pos_frac
        self.init_pos_frac = pos_frac


    def update(self):
        OvalEditBox.update(self)
        self.init_pos_frac = self.pos_frac

class GradientColorEditor(object):
    def __init__(self, prop_name, parent_shape):
        self.parent_shape  = parent_shape
        self.prop_name = prop_name
        self.gradient_color = self.parent_shape.get_prop_value(prop_name)
        self.edit_boxes = []
        self.selected_edit_box = None
        self.build_edit_boxes()

    def build_edit_boxes(self):
        if not self.gradient_color:
            return
        del self.edit_boxes[:]
        full_distance = self.gradient_color.get_full_distance()
        for color_point_index in range(len(self.gradient_color.color_points)):
            color_point = self.gradient_color.color_points[color_point_index]
            distance = self.gradient_color.get_distance_of(color_point_index)
            pos_frac = distance/full_distance
            edit_box = ColorPointBox(color_point_index, color_point, pos_frac)
            edit_box.parent_shape = self.parent_shape
            self.edit_boxes.append(edit_box)

    def update_color(self):
        self.gradient_color.get_pattern(forced=True)
        self.parent_shape.set_prop_value(self.prop_name, self.gradient_color)

    def select_item_at(self, point):
        point = self.parent_shape.parent_shape.abs_reverse_transform_point(point)
        for edit_box in self.edit_boxes:
            if edit_box.is_within(point):
                self.selected_edit_box = edit_box
                return
        self.selected_edit_box = None

    def move_active_item(self, start_point, end_point):
        if not self.selected_edit_box: return
        start_point = self.parent_shape.transform_point(start_point)
        end_point = self.parent_shape.transform_point(end_point)

        if self.selected_edit_box.color_point_index>0 and  \
            self.selected_edit_box.color_point_index<len(self.gradient_color.color_points)-1:
            index = self.selected_edit_box.color_point_index

            distance = end_point.distance(self.edit_boxes[0].point)
            full_distance = self.edit_boxes[-1].point.distance(self.edit_boxes[0].point)
            pos_frac = distance/full_distance
            if pos_frac<=self.edit_boxes[index-1].pos_frac or \
               pos_frac>=self.edit_boxes[index+1].pos_frac:
                return

            self.selected_edit_box.pos_frac = pos_frac
            length_x = self.edit_boxes[-1].point.x - self.edit_boxes[0].point.x
            length_y = self.edit_boxes[-1].point.y - self.edit_boxes[0].point.y

            self.selected_edit_box.point.x = self.edit_boxes[0].point.x + pos_frac*length_x
            self.selected_edit_box.point.y = self.edit_boxes[0].point.y + pos_frac*length_y
        elif self.selected_edit_box.color_point_index==0:
            diff_point = end_point.diff(start_point)
            edit_box_point = self.selected_edit_box.init_point.copy()
            edit_box_point.translate(diff_point.x, diff_point.y)

            old_distance = self.edit_boxes[-1].init_point.distance(self.edit_boxes[0].init_point)
            new_distance = self.edit_boxes[-1].point.distance(edit_box_point)

            scale = new_distance/old_distance
            if scale<(1-self.edit_boxes[1].pos_frac):
                return
            self.selected_edit_box.move_offset(diff_point.x, diff_point.y)

            length_x = self.edit_boxes[-1].point.x - self.edit_boxes[0].point.x
            length_y = self.edit_boxes[-1].point.y - self.edit_boxes[0].point.y

            for edit_box in self.edit_boxes[1:-1]:
                distance_back = edit_box.init_point.distance(self.edit_boxes[-1].init_point)
                edit_box.pos_frac = 1. - distance_back/new_distance
                edit_box.point.x = self.edit_boxes[0].point.x + edit_box.pos_frac*length_x
                edit_box.point.y = self.edit_boxes[0].point.y + edit_box.pos_frac*length_y

        elif self.selected_edit_box.color_point_index==len(self.gradient_color.color_points)-1:
            diff_point = end_point.diff(start_point)
            edit_box_point = self.selected_edit_box.init_point.copy()
            edit_box_point.translate(diff_point.x, diff_point.y)

            old_distance = self.edit_boxes[-1].init_point.distance(self.edit_boxes[0].init_point)
            new_distance = self.edit_boxes[0].point.distance(edit_box_point)

            scale = new_distance/old_distance
            if scale<self.edit_boxes[-2].pos_frac:
                return
            self.selected_edit_box.move_offset(diff_point.x, diff_point.y)

            length_x = self.edit_boxes[-1].point.x - self.edit_boxes[0].point.x
            length_y = self.edit_boxes[-1].point.y - self.edit_boxes[0].point.y

            for edit_box in self.edit_boxes[1:-1]:
                distance = edit_box.init_point.distance(self.edit_boxes[0].init_point)
                edit_box.pos_frac = distance/new_distance
                edit_box.point.x = self.edit_boxes[0].point.x + edit_box.pos_frac*length_x
                edit_box.point.y = self.edit_boxes[0].point.y + edit_box.pos_frac*length_y

        self.update_color()

    def end_movement(self):
        for edit_box in self.edit_boxes:
            edit_box.update()
        self.selected_edit_box = None

    def delete_point(self):
        if not self.selected_edit_box:
            return False
        color_point_index = self.selected_edit_box.color_point_index
        self.gradient_color.remove_color_point_at(color_point_index)
        self.build_edit_boxes()
        return True

    def insert_point_at(self, point):
        point = self.parent_shape.transform_point(point)
        inserted = False
        for i in range(1, len(self.gradient_color.color_points)):
            point2 = self.gradient_color.color_points[i].point
            point1 = self.gradient_color.color_points[i-1].point
            minx = min(point1.x, point2.x)
            maxx = max(point1.x, point2.x)
            miny = min(point1.y, point2.y)
            maxy = max(point1.y, point2.y)
            if minx<=point.x<=maxx and miny<=point.y<=maxy:
                frac = point.distance(point1)/point2.distance(point1)
                new_point = Point(
                    point1.x + (point2.x-point1.x)*frac,
                    point1.y + (point2.y-point1.y)*frac
                )
                self.gradient_color.insert_color_point_at(
                    i, self.gradient_color.color_points[i-1].color.copy(), new_point)
                inserted = True
                break
        if inserted:
            self.build_edit_boxes()
        return inserted

    def choose_color(self):
        if not self.selected_edit_box:
            return
        color = self.selected_edit_box.fill_color
        dialog = Gtk.ColorChooserDialog()
        rgba = Gdk.RGBA(*color.get_array())
        dialog.set_rgba(rgba)
        res = True
        if dialog.run() == Gtk.ResponseType.OK:
            rgba = dialog.get_rgba()
            new_color = Color(rgba.red, rgba.green, rgba.blue, rgba.alpha)
            color.copy_from(new_color)
            res = True
            self.update_color()
        dialog.destroy()
        return res

    def draw(self, ctx):
        ctx.save()
        self.parent_shape.pre_draw(ctx)
        for i in range(len(self.edit_boxes)):
            edit_box = self.edit_boxes[i]
            if i == 0:
                ctx.move_to(edit_box.point.x, edit_box.point.y)
            else:
                ctx.line_to(edit_box.point.x, edit_box.point.y)
        ctx.restore()
        draw_stroke(ctx, 1)
        for edit_box in self.edit_boxes:
            if edit_box == self.selected_edit_box:
                draw_frac = 1.
            else:
                draw_frac = .5
            edit_box.reposition(None)
            edit_box.draw_edit_box(ctx, draw_frac)
