from ..commons import *
from ..commons.draw_utils import draw_fill
from ..shapes import *
from ..settings import EditingChoice

OUTER = "OUTER"
INNER = "INNER"

ROTATION_TOP_LEFT = "ROTATION_TOP_LEFT"
ROTATION_TOP_RIGHT = "ROTATION_TOP_RIGHT"
ROTATION_BOTTOM_RIGHT = "ROTATION_BOTTOM_RIGHT"
ROTATION_LEFT_BOTTOM = "ROTATION_LEFT_BOTTOM"
RESIZING_TOP = "RESIZING_TOP"
RESIZING_RIGHT = "RESIZING_RIGHT"
RESIZING_BOTTOM = "RESIZING_BOTTOM"
RESIZING_LEFT = "RESIZING_LEFT"
RESIZING_BOTTOM_RIGHT = "RESIZING_BOTTOM_RIGHT"
ANCHOR = "ANCHOR"

SELECTED_EDIT_BOX_COLOR = Color.from_html("00b100")

class ControlEditBox(OvalEditBox):
    def __init__(self, percent_point, curve_index, bezier_point_index, control_index):
        if control_index == 0:
            fill_color = Color(1,1,0,1)
        else:
            fill_color = Color(1,0,0,1)
        OvalEditBox.__init__(self, percent_point, radius=10, fill_color=fill_color, is_percent=True)
        self.curve_index = curve_index
        self.bezier_point_index = bezier_point_index
        self.control_index = control_index
        self.is_start = False

class DestEditBox(OvalEditBox):
    def __init__(self, percent_point, curve_index, bezier_point_index):
        OvalEditBox.__init__(self, percent_point)
        self.curve_index = curve_index
        self.bezier_point_index = bezier_point_index
        self.is_start = False

class OriginEditBox(OvalEditBox):
    def __init__(self, percent_point, curve_index):
        OvalEditBox.__init__(self, percent_point)
        self.curve_index = curve_index
        self.bezier_point_index = -1
        self.is_start = True

class PolygonPointEditBox(OvalEditBox):
    def __init__(self, percent_point, polygon_index, point_index):
        OvalEditBox.__init__(self, percent_point)
        self.polygon_index = polygon_index
        self.point_index = point_index
        self.is_start = (point_index == 0)

class ShapeEditor(object):
    def __init__(self, shape):
        self.shape = shape
        self.selected_edit_boxes = []
        self.edit_box_can_move = False
        self.init_shape = shape.copy()

        self.all_edit_box_list = []
        self.named_edit_boxes = dict()
        self.outer_edit_boxes = []
        self.inner_edit_boxes = []
        self.rotation_edit_boxes = []

        self.moveable_point_edit_boxes = []
        self.curve_point_lines = []
        self.breakable_point_edit_boxes = []
        self.joinable_point_edit_boxes = []
        self.deletable_point_edit_boxes = []

        margin = MARGIN
        self.outline_edit_box = OutlineEditBox(self.shape)
        outline_color = (0, 0, 0, 1)
        if isinstance(self.shape, CurvePointGroupShape):
            outline_color = Color.from_html("73D216")
        self.outline_edit_box.border_color = outline_color

        self.new_edit_box(OvalEditBox(Point(0.0, 0.0), offset=Point(-margin, -margin)),
                    OUTER, ROTATION_TOP_LEFT, self.rotation_edit_boxes)
        self.new_edit_box(OvalEditBox(Point(1.0, 0.0), offset=Point(margin, -margin)),
                    OUTER, ROTATION_TOP_RIGHT, self.rotation_edit_boxes)
        #self.new_edit_box(OvalEditBox(Point(1.0, 1.0), offset=Point(margin, margin)),
        #            OUTER, ROTATION_BOTTOM_RIGHT, self.rotation_edit_boxes)
        self.new_edit_box(OvalEditBox(Point(0.0, 1.0), offset=Point(-margin, margin)),
                    OUTER, ROTATION_LEFT_BOTTOM, self.rotation_edit_boxes)

        self.new_edit_box(RectEditBox(Point(0.5, 0.0), angle=0, offset=Point(0, -margin)),
                          OUTER, RESIZING_TOP)
        self.new_edit_box(RectEditBox(Point(1.0, 0.5), angle=90, offset=Point(margin, 0)),
                          OUTER, RESIZING_RIGHT)
        self.new_edit_box(RectEditBox(Point(0.5, 1.0), angle=180, offset=Point(0, margin)),
                          OUTER, RESIZING_BOTTOM)
        self.new_edit_box(RectEditBox(Point(0.0, 0.5), angle=270, offset=Point(-margin, 0)),
                          OUTER, RESIZING_LEFT)
        self.new_edit_box(RectEditBox(Point(1.0, 1.0), angle=0,
                          offset=Point(margin, margin), height=10.),
                          OUTER, RESIZING_BOTTOM_RIGHT)

        self.new_edit_box(AnchorEditBox(self.shape), INNER, ANCHOR)

        control_1_fill_color = Color(1,1,0,1)
        control_2_fill_color = Color(1,0,0,1)
        if isinstance(shape, CurveShape) and shape.show_points:
            for curve_index in range(len(self.shape.curves)):
                curve = self.shape.curves[curve_index]
                last_dest_eb = None
                origin_eb = self.new_edit_box(OriginEditBox(curve.origin, curve_index), INNER)
                self.deletable_point_edit_boxes.append(origin_eb)
                if not curve.closed:
                    last_dest_eb = origin_eb
                    self.moveable_point_edit_boxes.append(origin_eb)
                    self.joinable_point_edit_boxes.append(origin_eb)

                first_control_1_eb = None
                for bpi in range(len(curve.bezier_points)):
                    bezier_point = curve.bezier_points[bpi]
                    dest_eb = self.new_edit_box(DestEditBox(
                        bezier_point.dest, curve_index, bpi), INNER)
                    control_1_eb = self.new_edit_box(ControlEditBox(
                        bezier_point.control_1, curve_index, bpi, 0), INNER)
                    control_2_eb = self.new_edit_box(ControlEditBox(
                        bezier_point.control_2, curve_index, bpi, 1), INNER)
                    if last_dest_eb:
                        last_dest_eb.add_linked_edit_box(control_1_eb)
                    dest_eb.add_linked_edit_box(control_2_eb)

                    self.deletable_point_edit_boxes.append(dest_eb)

                    self.moveable_point_edit_boxes.append(dest_eb)
                    self.moveable_point_edit_boxes.append(control_1_eb)
                    self.moveable_point_edit_boxes.append(control_2_eb)
                    self.breakable_point_edit_boxes.append(dest_eb)

                    if bpi == 0:
                        if curve.closed:
                            prev_dest_point = curve.bezier_points[-1].dest
                        else:
                            prev_dest_point = curve.origin
                    else:
                        prev_dest_point = curve.bezier_points[bpi-1].dest
                    if prev_dest_point:
                        self.new_curve_point_line(bezier_point.control_1, prev_dest_point)
                    self.new_curve_point_line(bezier_point.control_2, bezier_point.dest)

                    last_dest_eb = dest_eb
                    if first_control_1_eb is None:
                        first_control_1_eb = control_1_eb

                    if bpi<len(curve.bezier_points)-1 or curve.closed:
                        self.breakable_point_edit_boxes.append(dest_eb)
                    if bpi == len(curve.bezier_points)-1 and not curve.closed:
                        self.joinable_point_edit_boxes.append(control_1_eb)
                        self.joinable_point_edit_boxes.append(control_2_eb)
                        self.joinable_point_edit_boxes.append(dest_eb)

                if curve.closed and last_dest_eb and first_control_1_eb:
                    last_dest_eb.add_linked_edit_box(first_control_1_eb)
                    last_dest_eb.add_linked_edit_box(origin_eb)
                    last_dest_eb.origin_eb = origin_eb#save the origin editbox, used in alignment
                    self.all_edit_box_list.remove(first_control_1_eb)
                    self.all_edit_box_list.append(first_control_1_eb)

        elif isinstance(shape, PolygonShape):
            polygon_shape = shape
            for polygon_index in range(len(polygon_shape.polygons)):
                polygon = polygon_shape.polygons[polygon_index]
                for point_index in range(len(polygon.points)):
                    point = polygon.points[point_index]
                    point_eb = self.new_edit_box(PolygonPointEditBox(
                        point, polygon_index, point_index), INNER)
                    self.moveable_point_edit_boxes.append(point_eb)
                    if polygon.closed or point_index>0 or point_index<len(polygon.points)-1:
                        self.breakable_point_edit_boxes.append(point_eb)
                    if not polygon.closed and (point_index == 0 or point_index==len(polygon.points)-1):
                        self.joinable_point_edit_boxes.append(point_eb)
                    self.deletable_point_edit_boxes.append(point_eb)

    def update_edit_boxes(self):
        for edit_box in self.moveable_point_edit_boxes:
            edit_box.update()

    def has_selected_box(self):
        return len(self.selected_edit_boxes)>0

    def new_edit_box(self, edit_box, outer_inner, name=None, in_list=None):
        self.all_edit_box_list.append(edit_box)
        if name is not None:
            if name in self.named_edit_boxes:
                raise Exception("{0} is already present in edit_boxes dict".format(name))
            self.named_edit_boxes[name] = edit_box
        if outer_inner == OUTER:
            self.outer_edit_boxes.append(edit_box)
        elif outer_inner == INNER:
            self.inner_edit_boxes.append(edit_box)
        if in_list is not None:
            in_list.append(edit_box)
        edit_box.parent_shape = self.shape
        return edit_box

    def new_curve_point_line(self, point_1, point_2):
        line = EditLine(point_1, point_2)
        self.curve_point_lines.append(line)
        return line

    def get_edit_box_at(self, point):
        point = point.copy()
        point = self.shape.parent_shape.abs_reverse_transform_point(point)
        for edit_box in reversed(self.all_edit_box_list):
            if isinstance(edit_box, ControlEditBox) and EditingChoice.HIDE_CONTROL_POINTS:
                continue
            if edit_box.is_within(point):
                return edit_box
        return None

    def deselect_all(self):
        del self.selected_edit_boxes[:]

    def get_selected_moveable_point_indices(self):
        items = dict()
        if not isinstance(self.shape, CurveShape): return items
        for edit_box in self.selected_edit_boxes:
            if edit_box not in self.moveable_point_edit_boxes:
                continue
            if edit_box.curve_index not in items:
                items[edit_box.curve_index] = dict()
            items[edit_box.curve_index][edit_box.bezier_point_index]=edit_box.bezier_point_index
        return items

    def select_items_inside_rect(self, rect):
        if not (isinstance(self.shape, CurveShape) or \
                isinstance(self.shape, PolygonShape)): return False
        del self.selected_edit_boxes[:]
        for edit_box in self.moveable_point_edit_boxes:
            if isinstance(edit_box, ControlEditBox) and EditingChoice.HIDE_CONTROL_POINTS:
                continue
            point = edit_box.point.copy()
            if edit_box.is_percent:
                point.scale(self.shape.width, self.shape.height)
            point = self.shape.reverse_transform_point(point)
            if rect.left<=point.x and point.x<=rect.left+rect.width and \
               rect.top<=point.y and point.y<=rect.top+rect.height:
                self.selected_edit_boxes.append(edit_box)
        return len(self.selected_edit_boxes)>0

    def select_item_at(self, point, multi_select):
        if not multi_select and len(self.selected_edit_boxes)>1:
            return

        selected_edit_box = self.get_edit_box_at(point)
        if selected_edit_box is None and not EditingChoice.HIDE_CONTROL_POINTS and \
            len(self.selected_edit_boxes) == 0 and isinstance(self.shape, CurveShape):
            point = self.shape.transform_point(point)
            found = self.shape.find_point_location(point)
            if found:
                curve_index, bezier_point_index, t = found
                control_index = 1 if t>.5 else 0
                for edit_box in self.moveable_point_edit_boxes:
                    if not isinstance(edit_box, ControlEditBox): continue
                    if edit_box.curve_index == curve_index and \
                       edit_box.bezier_point_index == bezier_point_index and \
                       edit_box.control_index == control_index:
                       selected_edit_box = edit_box
                       break

        if selected_edit_box:
            if multi_select and \
                (isinstance(self.shape, CurveShape) or isinstance(self.shape, PolygonShape)):

                if selected_edit_box in self.selected_edit_boxes:
                    self.selected_edit_boxes.remove(selected_edit_box)
                    if len(self.selected_edit_boxes) == 1:
                        del self.selected_edit_boxes[:]
                else:
                    self.selected_edit_boxes.append(selected_edit_box)
            else:
                del self.selected_edit_boxes[:]
                self.selected_edit_boxes.append(selected_edit_box)
        else:
            del self.selected_edit_boxes[:]
        self.edit_box_can_move = (len(self.selected_edit_boxes)>0)

    def draw(self, ctx):
        padding = 10+self.shape.get_border_width()*.5
        outer_rect = self.shape.get_outline(padding*0)

        self.outline_edit_box.draw(ctx)

        self.named_edit_boxes[ANCHOR].set_point(self.shape.anchor_at)

        for edit_box in self.outer_edit_boxes:
            edit_box.reposition(outer_rect)

        inner_rect = self.shape.get_outline(0)
        for edit_box in self.inner_edit_boxes:
            edit_box.reposition(inner_rect)

        if False and isinstance(self.shape, CurveShape) and len(self.shape.curves[0].bezier_points)>20:
            return

        if not EditingChoice.HIDE_CONTROL_POINTS:
            for line in self.curve_point_lines:
                ctx.save()
                self.shape.pre_draw(ctx)
                line.pre_draw(ctx)
                ctx.scale(self.shape.width, self.shape.height)
                line.draw_line(ctx)
                ctx.restore()
                line.draw_border(ctx)

        for edit_box in self.all_edit_box_list:
            draw_frac = 1. if edit_box in self.selected_edit_boxes else .5
            if isinstance(edit_box, ControlEditBox) and EditingChoice.HIDE_CONTROL_POINTS:
                continue
            ctx.save()
            edit_box.draw_edit_box(ctx, draw_frac)
            ctx.restore()

    def move_active_item(self, start_point, end_point):
        if self.selected_edit_boxes:
            rel_start_point = self.init_shape.transform_point(start_point)
            rel_end_point = self.init_shape.transform_point(end_point)
            rel_dpoint = rel_end_point.diff(rel_start_point)

            for edit_box in self.selected_edit_boxes:
                if edit_box == self.named_edit_boxes[RESIZING_BOTTOM]:
                    if isinstance(self.shape, MultiShape):
                        self.shape.post_scale_y = self.init_shape.post_scale_y * \
                        ((self.init_shape.height+rel_dpoint.y)/self.init_shape.height)
                    else:
                        self.shape.set_height(self.init_shape.height+rel_dpoint.y)

                elif edit_box == self.named_edit_boxes[RESIZING_RIGHT]:
                    if isinstance(self.shape, MultiShape):
                        self.shape.post_scale_x = self.init_shape.post_scale_x * \
                        ((self.init_shape.width+rel_dpoint.x)/self.init_shape.width)
                        self.shape.anchor_at.x = self.init_shape.anchor_at.x * \
                            (self.init_shape.post_scale_x/self.shape.post_scale_x)
                    else:
                        self.shape.set_width(self.init_shape.width+rel_dpoint.x)

                elif edit_box == self.named_edit_boxes[RESIZING_TOP]:
                    init_abs_anchor_at = self.init_shape.get_abs_anchor_at()
                    if isinstance(self.shape, MultiShape):
                        self.shape.post_scale_y = self.init_shape.post_scale_y * \
                        ((self.init_shape.height-rel_dpoint.y)/self.init_shape.height)

                        self.shape.anchor_at.y = self.init_shape.height-\
                            (self.init_shape.height-self.init_shape.anchor_at.y)*\
                            (self.init_shape.post_scale_y/self.shape.post_scale_y)
                    else:
                        self.shape.anchor_at.y = self.init_shape.anchor_at.y - rel_dpoint.y
                        self.shape.set_height(self.init_shape.height-rel_dpoint.y)
                    self.shape.move_to(init_abs_anchor_at.x, init_abs_anchor_at.y)

                elif edit_box == self.named_edit_boxes[RESIZING_LEFT]:
                    init_abs_anchor_at = self.init_shape.get_abs_anchor_at()
                    if isinstance(self.shape, MultiShape):
                        self.shape.post_scale_x = self.init_shape.post_scale_x * \
                        ((self.init_shape.width-rel_dpoint.x)/self.init_shape.width)

                        self.shape.anchor_at.x = self.init_shape.width-\
                            (self.init_shape.width-self.init_shape.anchor_at.x)*\
                            (self.init_shape.post_scale_x/self.shape.post_scale_x)
                    else:
                        self.shape.anchor_at.x = self.init_shape.anchor_at.x - rel_dpoint.x
                        self.shape.set_width(self.init_shape.width-rel_dpoint.x)
                    self.shape.move_to(init_abs_anchor_at.x, init_abs_anchor_at.y)

                elif edit_box == self.named_edit_boxes[RESIZING_BOTTOM_RIGHT]:
                    if isinstance(self.shape, MultiShape):
                        self.shape.post_scale_x = self.init_shape.post_scale_x * \
                        ((self.init_shape.width+rel_dpoint.x)/self.init_shape.width)
                        self.shape.anchor_at.x = self.init_shape.anchor_at.x *\
                            (self.init_shape.post_scale_x/self.shape.post_scale_x)

                        self.shape.post_scale_y = self.init_shape.post_scale_y * \
                            ((self.init_shape.height+rel_dpoint.y)/self.init_shape.height)
                        self.shape.anchor_at.y = self.init_shape.height-\
                            (self.init_shape.height-self.init_shape.anchor_at.y)*\
                            (self.init_shape.post_scale_y/self.shape.post_scale_y)
                    else:
                        self.shape.set_width(self.init_shape.width+rel_dpoint.x)
                        self.shape.set_height(self.init_shape.height+rel_dpoint.y)

                elif edit_box == self.named_edit_boxes[ANCHOR]:
                    edit_box.move_offset(rel_dpoint.x, rel_dpoint.y)

                elif edit_box in self.rotation_edit_boxes:
                    init_abs_anchor_at = self.init_shape.get_abs_anchor_at()
                    rel_anch_start_point = start_point.diff(init_abs_anchor_at)
                    rel_anch_end_point = end_point.diff(init_abs_anchor_at)
                    dangle = rel_anch_end_point.get_angle() - rel_anch_start_point.get_angle()
                    self.shape.set_angle(self.init_shape.angle+dangle)

                elif edit_box in self.moveable_point_edit_boxes:
                    percent_point = Point(rel_dpoint.x/self.shape.width, rel_dpoint.y/self.shape.height)
                    if False and \
                        isinstance(self.shape, PolygonShape) and len(self.shape.polygons[0].points)>6:
                        span = 5
                        for i in range(-span, span, 1):
                            frac = (span-abs(i))*1./span
                            pp = percent_point.copy()
                            pp.x *= frac
                            pp.y *= frac
                            point_index = edit_box.point_index + i
                            for edb in self.moveable_point_edit_boxes:
                                if edb.polygon_index != edit_box.polygon_index: continue
                                if edb.point_index != point_index: continue
                                edb.move_offset(pp.x, pp.y)
                                break
                    edit_box.move_offset(percent_point.x, percent_point.y)
            self.named_edit_boxes[ANCHOR].set_point(self.shape.anchor_at)
        elif self.edit_box_can_move is False:
            if not EditingChoice.LOCK_SHAPE_MOVEMENT and self.shape.moveable:
                diff_point = end_point.diff(start_point)
                init_abs_anchor_at = self.init_shape.get_abs_anchor_at()
                self.shape.move_to(init_abs_anchor_at.x+diff_point.x, init_abs_anchor_at.y+diff_point.y)

    def end_movement(self):
        self.edit_box_can_move = (len(self.selected_edit_boxes)>0)
        if isinstance(self.shape, CurveShape) or isinstance(self.shape, PolygonShape):
            self.shape.fit_size_to_include_all()
        elif isinstance(self.shape, TextShape):
            self.shape.readjust_sizes()
        self.init_shape = self.shape.copy()
        for edit_box in self.all_edit_box_list:
            edit_box.update()

    def insert_break(self):
        if not (isinstance(self.shape, CurveShape) or \
                isinstance(self.shape, PolygonShape)): return False
        if len(self.selected_edit_boxes) != 1: return False
        if self.selected_edit_boxes[0] not in self.breakable_point_edit_boxes: return False
        if isinstance(self.shape, CurveShape):
            return self.shape.insert_break_at(
                self.selected_edit_boxes[0].curve_index,
                self.selected_edit_boxes[0].bezier_point_index
            )
        elif isinstance(self.shape, PolygonShape):
            return self.shape.insert_break_at(
                self.selected_edit_boxes[0].polygon_index,
                self.selected_edit_boxes[0].point_index
            )

    def join_points(self):
        if not (isinstance(self.shape, CurveShape) or \
                isinstance(self.shape, PolygonShape)): return False
        if len(self.selected_edit_boxes) != 2: return False
        if self.selected_edit_boxes[0] not in self.joinable_point_edit_boxes: return False
        if self.selected_edit_boxes[1] not in self.joinable_point_edit_boxes: return False
        if isinstance(self.shape, CurveShape):
            return self.shape.join_points(
                self.selected_edit_boxes[0].curve_index,
                self.selected_edit_boxes[0].is_start,
                self.selected_edit_boxes[1].curve_index,
                self.selected_edit_boxes[1].is_start
            )
        elif isinstance(self.shape, PolygonShape):
            return self.shape.join_points(
                self.selected_edit_boxes[0].polygon_index,
                self.selected_edit_boxes[0].is_start,
                self.selected_edit_boxes[1].polygon_index,
                self.selected_edit_boxes[1].is_start
            )

    def create_point_group(self):
        if not (isinstance(self.shape, CurveShape) or \
                isinstance(self.shape, PolygonShape)): return False
        if len(self.selected_edit_boxes) < 2: return False
        if isinstance(self.shape, CurveShape):
            curve_point_group = CurvePointGroup()
            for edit_box in self.selected_edit_boxes:
                if isinstance(edit_box, DestEditBox):
                    point_type = CurvePoint.POINT_TYPE_DEST
                elif isinstance(edit_box, ControlEditBox):
                    if edit_box.control_index == 0:
                        point_type = CurvePoint.POINT_TYPE_CONTROL_1
                    elif edit_box.control_index == 1:
                        point_type = CurvePoint.POINT_TYPE_CONTROL_2

                curve_point = CurvePoint(edit_box.curve_index, edit_box.bezier_point_index, point_type)
                curve_point_group.add_point(curve_point)
            del self.selected_edit_boxes[:]
            return self.shape.add_point_group(curve_point_group)
        return False

    def align_points(self, x_dir, y_dir):
        for i in range(1, len(self.selected_edit_boxes), 1):
            edit_box = self.selected_edit_boxes[i]
            if x_dir:
                edit_box.point.x = self.selected_edit_boxes[0].point.x
            if y_dir:
                edit_box.point.y = self.selected_edit_boxes[0].point.y
            if isinstance(edit_box, DestEditBox) and isinstance(self.shape, CurveShape):
                curve = self.shape.curves[edit_box.curve_index]
                if curve.closed and \
                   edit_box.bezier_point_index == len(curve.bezier_points)-1:
                   edit_box.origin_eb.point.x = edit_box.point.x
                   edit_box.origin_eb.point.y = edit_box.point.y
                   edit_box.origin_eb.update()
            edit_box.update()

    def delete_point(self):
        if not (isinstance(self.shape, CurveShape) or \
                isinstance(self.shape, PolygonShape)): return False
        if len(self.selected_edit_boxes) == 0: return False

        if isinstance(self.shape, CurveShape):
            items = dict()
            for edit_box in self.selected_edit_boxes:
                if edit_box not in self.deletable_point_edit_boxes:
                    continue
                if edit_box.curve_index not in items:
                    items[edit_box.curve_index] = dict()
                items[edit_box.curve_index][edit_box.bezier_point_index]=edit_box.bezier_point_index
            delete_count = 0
            for curve_index in reversed(sorted(items.keys())):
                for bezier_point_index in reversed(sorted(items[curve_index].keys())):
                    if self.shape.delete_point_at(curve_index, bezier_point_index):
                        delete_count += 1
            return delete_count>0

        elif isinstance(self.shape, PolygonShape):
            items = dict()
            for edit_box in self.selected_edit_boxes:
                if edit_box not in self.deletable_point_edit_boxes:
                    continue
                if edit_box.polygon_index not in items:
                    items[edit_box.polygon_index] = dict()
                items[edit_box.polygon_index][edit_box.point_index]=edit_box.point_index
            delete_count = 0
            polygon_count = len(self.shape.polygons)
            for polygon_index in reversed(sorted(items.keys())):
                for point_index in reversed(sorted(items[polygon_index].keys())):
                    if self.shape.delete_point_at(polygon_index, point_index):
                        delete_count += 1
                        if polygon_count != len(self.shape.polygons):
                            polygon_count = len(self.shape.polygons)
                            break
            return delete_count>0

    def extend_point(self):
        if not isinstance(self.shape, PolygonShape): return None
        if len(self.selected_edit_boxes) != 1: return None
        if self.selected_edit_boxes[0] not in self.joinable_point_edit_boxes: return None
        return self.shape.extend_point(
            self.selected_edit_boxes[0].polygon_index,
            self.selected_edit_boxes[0].is_start,
        )
