from ..commons import *
from ..shapes import CurveShape, OvalEditBox, EditLine

class CurveShapeCreator(object):
    def __init__(self, point):
        self.shape = CurveShape(Point(0, 0), Color(0,0,0,1), 1, Color(1,1,1,0), 1, 1)
        self.curve = Curve(origin=point.copy())
        self.shape.add_curve(self.curve)
        self.bezier_point = None
        self.shape.move_to(point.x, point.y)

        self.edit_boxes = []
        ctc = Color(1,1,0,1)
        self.edit_boxes.append(OvalEditBox(point.copy(), radius=5, is_percent = True, fill_color=ctc))
        self.edit_boxes.append(OvalEditBox(point.copy(), radius=5, is_percent = True, fill_color=ctc))
        self.edit_boxes.append(OvalEditBox(point.copy(), radius=5, is_percent = True))

        self.edit_lines = []
        self.edit_lines.append(EditLine(Point(0, 0), Point(0, 0)))
        self.edit_lines.append(EditLine(Point(0, 0), Point(0, 0)))

    def set_relative_to(self, multi_shape):
        self.shape.move_to(multi_shape.translation.x, multi_shape.translation.y)
        for edit_box in self.edit_boxes:
            edit_box.parent_shape = multi_shape
        rect = self.shape.get_outline(0)

        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

    def begin_movement(self, point):
        self.move_dest = False
        self.do_movement(point, point)

    def do_movement (self, start_point, end_point):
        if self.bezier_point is None: return
        #rel_end_point = self.shape.transform_point(end_point)
        rel_end_point = end_point
        scaled_rel_end_point = rel_end_point.copy()
        scaled_rel_end_point.scale(self.shape.width, self.shape.height)

        if self.move_dest:
            control_2_diff_point = self.bezier_point.control_2.diff(self.bezier_point.dest)
            self.bezier_point.dest.copy_from(scaled_rel_end_point)
            self.bezier_point.control_2.assign(
                    self.bezier_point.dest.x+control_2_diff_point.x,
                    self.bezier_point.dest.y+control_2_diff_point.y)
        else:
            rel2_end_point = scaled_rel_end_point.diff(self.bezier_point.dest)
            self.bezier_point.control_2.assign(
                self.bezier_point.dest.x-rel2_end_point.x,
                self.bezier_point.dest.y-rel2_end_point.y)

        self.edit_boxes[0].set_point(self.bezier_point.control_2)
        self.edit_boxes[1].set_point(scaled_rel_end_point)
        self.edit_boxes[2].set_point(self.bezier_point.dest)

        rect = self.shape.get_outline(0)

        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

        self.edit_lines[0].set_points(self.edit_boxes[0].point, self.edit_boxes[2].point)
        self.edit_lines[1].set_points(self.edit_boxes[1].point, self.edit_boxes[2].point)

    def get_shape(self):
        return self.shape

    def draw(self, ctx):
        for edit_line in self.edit_lines:
            ctx.save()
            self.shape.pre_draw(ctx)
            edit_line.draw_line(ctx)
            ctx.restore()
            edit_line.draw_border(ctx)

        for edit_box in self.edit_boxes:
            edit_box.draw(ctx)

    def end_movement(self):
        if self.bezier_point is None:
            last_point = self.curve.origin
        else:
            last_point = self.bezier_point.dest
        self.bezier_point = BezierPoint(last_point.copy(), last_point.copy(), last_point.copy())
        self.curve.add_bezier_point(self.bezier_point)
        self.move_dest = True
        return False

    def close_down(self):
        self.shape.fit_size_to_include_all()

        self.curve.remove_bezier_point(self.bezier_point)
        dx = self.curve.bezier_points[-1].dest.x - self.curve.origin.x
        dy = self.curve.bezier_points[-1].dest.y - self.curve.origin.y

        dx *= self.shape.width
        dy *= self.shape.height

        spread = 5
        if abs(dx)<spread and abs(dy)<spread:
            self.curve.set_closed(True)
            self.curve.bezier_points[-1].dest.copy_from(self.curve.origin)

        self.shape.fit_size_to_include_all()
        self.shape.anchor_at.x = self.shape.width*.5
        self.shape.anchor_at.y = self.shape.height*.5
