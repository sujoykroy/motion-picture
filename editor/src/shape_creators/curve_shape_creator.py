from ..commons import *
from ..shapes import CurveShape, OvalEditBox, EditLine
from ..settings import config

class CurveShapeCreator(object):
    @classmethod
    def create_blank(cls, point):
        shape = CurveShape(Point(0, 0), Color(0,0,0,1),
                        config.DEFAULT_BORDER_WIDTH, Color(1,1,1,0), 1, 1)
        return cls(shape, -1, -1, new_shape=True)

    def __init__(self, shape, curve_index, bezier_point_index, new_shape=False):
        self.shape = shape
        self.curve = None
        self.bezier_point = None
        self.move_dest = False
        self.new_shape = new_shape

        if shape.curves:
            self.curve = shape.curves[curve_index]
            if (-1<bezier_point_index<len(self.curve.bezier_points)) or \
               (bezier_point_index == -1 and len(self.curve.bezier_points)>0):
                self.bezier_point = self.curve.bezier_points[bezier_point_index]
                self.move_dest = True

        self.edit_boxes = []
        ctc = Color(1,1,0,1)
        self.edit_boxes.append(OvalEditBox(Point(0, 0), radius=5, is_percent = True, fill_color=ctc))
        self.edit_boxes.append(OvalEditBox(Point(0, 0), radius=5, is_percent = True, fill_color=ctc))
        self.edit_boxes.append(OvalEditBox(Point(0, 0), radius=5, is_percent = True))

        self.edit_lines = []
        self.edit_lines.append(EditLine(Point(0, 0), Point(0, 0)))
        self.edit_lines.append(EditLine(Point(0, 0), Point(0, 0)))

    def set_relative_to(self, multi_shape):
        if self.new_shape:
            self.shape.move_to(0, 0)
        for edit_box in self.edit_boxes:
            edit_box.parent_shape = multi_shape
        for edit_line in self.edit_lines:
            edit_line.parent_shape = multi_shape
        rect = self.shape.get_outline(0)

        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

    def begin_movement(self, point):
        self.move_dest = False
        self.do_movement(point, point)

    def _reverse_transform_point(self, point):
        point = point.copy()
        point.scale(self.shape.width, self.shape.height)
        return self.shape.reverse_transform_locked_shape_point(point)

    def do_movement (self, start_point, end_point):
        if self.curve is None:
            self.curve = Curve(origin=self.shape.transform_locked_shape_point(
                        end_point, exclude_last=False))
            self.shape.add_curve(self.curve)
            return
        if self.bezier_point is None:
            return
        end_point = self.shape.transform_locked_shape_point(end_point, exclude_last=False)
        end_point.scale(1./self.shape.width, 1./self.shape.height)

        if self.move_dest:
            control_2_diff_point = self.bezier_point.control_2.diff(self.bezier_point.dest)
            self.bezier_point.dest.copy_from(end_point)
            self.bezier_point.control_2.assign(
                    self.bezier_point.dest.x+control_2_diff_point.x,
                    self.bezier_point.dest.y+control_2_diff_point.y)
        else:
            self.bezier_point.control_2.assign(
                2*self.bezier_point.dest.x-end_point.x,
                2*self.bezier_point.dest.y-end_point.y
            )

        self.edit_boxes[0].set_point(self._reverse_transform_point(self.bezier_point.control_2))
        self.edit_boxes[1].set_point(self._reverse_transform_point(end_point))
        self.edit_boxes[2].set_point(self._reverse_transform_point(self.bezier_point.dest))

        rect = self.shape.get_outline(0)

        for edit_box in self.edit_boxes:
            edit_box.reposition(rect)

        self.edit_lines[0].set_points(self.bezier_point.control_2, self.bezier_point.dest)
        self.edit_lines[1].set_points(end_point, self.bezier_point.dest)

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
            edit_box.draw_edit_box(ctx)

    def end_movement(self):
        if self.bezier_point is None:
            last_point = self.curve.origin
        else:
            last_point = self.bezier_point.dest
        bezier_point = BezierPoint(last_point.copy(), last_point.copy(), last_point.copy())
        self.curve.add_bezier_point(bezier_point)
        self.bezier_point = self.curve.bezier_points[-1]
        self.move_dest = True
        return False

    def close_down(self):
        self.shape.fit_size_to_include_all()

        self.curve.remove_bezier_point_index(-1)
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
