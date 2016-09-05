from gi.repository import GdkPixbuf
import os

from shape_editor import ShapeEditor

from ..commons import *
from ..commons.draw_utils import *

from ..shapes import *
from ..shape_creators import *
from guides import *
from ..tasks import *
from .. import settings
from ..settings import EditingChoice
from ..document import Document

class ScrollableArea(object):
    def __init__(self):
        self.width = 1
        self.height = 1
        self.offset_x = 0
        self.offset_y = 0

class ShapeManager(object):
    def __init__(self, multi_shape, doc):
        self.doc = doc
        self.multi_shape = multi_shape
        self.document_area_box = RectangleShape(
                anchor_at=Point(doc.width*.5, doc.height*.5),
                border_color = "cccccc",
                border_width = 1,
                fill_color= "ffffff",
                width = doc.width, height = doc.height, corner_radius=2)
        self.document_area_box_selected = False
        self.init_document_area_box = None
        self.scrollable_area = ScrollableArea()
        self.shape_editor = None
        self.shape_creator = None
        self.shapes = ShapeList(multi_shape.shapes)
        self.current_task = None

        self.guides = doc.guides
        for guide in self.guides:
            guide.parent_shape = self.document_area_box
        self.selected_guide = None

        self.out_width = doc.width
        self.out_height = doc.height

    def reload_shapes(self):
        self.delete_shape_editor()
        self.shape_creator = None
        self.shapes = ShapeList(self.multi_shape.shapes)

    def get_selected_shape(self):
        if self.shape_editor: return self.shape_editor.shape
        return None

    def get_selected_edit_box(self):
        if self.shape_editor:
            if self.shape_editor.selected_edit_boxes:
                return self.shape_editor.selected_edit_boxes[0]
        return None

    def has_shape_creator(self):
        return self.shape_creator is not None

    def has_designable_multi_shape_selected(self):
        if self.shape_editor is None: return False
        if isinstance(self.shape_editor.shape, MultiSelectionShape): return False
        return isinstance(self.shape_editor.shape, MultiShape)


    def is_flippable_shape_selected(self):
        if self.shape_editor is None: return False
        if isinstance(self.shape_editor.shape, MultiSelectionShape): return False
        return True

    def has_no_shape_selected(self):
        return self.shape_editor is None

    def has_curve_shape_selected(self):
        if self.shape_editor is None: return False
        return isinstance(self.shape_editor.shape, CurveShape)

    def selected_shape_supports_point_insert(self):
        if self.shape_editor is None: return False
        if isinstance(self.shape_editor.shape, CurveShape): return True
        if isinstance(self.shape_editor.shape, PolygonShape): return True
        return False

    def has_multi_selection(self):
        if self.shape_editor is None: return False
        return isinstance(self.shape_editor.shape, MultiSelectionShape)

    def place_shape_at_zero_position(self, shape):
        shape.move_to(self.multi_shape.translation.x, self.multi_shape.translation.y)

    def add_shape(self, shape):
        if not isinstance(shape, MultiSelectionShape):
            self.multi_shape.add_shape(shape)
        shape.parent_shape = self.multi_shape
        self.shapes.add(shape)

    def remove_shape(self, shape):
        self.shapes.remove(shape)
        self.multi_shape.remove_shape(shape)

    def rename_shape(self, shape, name):
        if self.mult_shape.rename_name(shape, name):
            return self.shapes.rename(shape, name)
        return False

    def get_shape_at(self, point, multi_select):
        for shape in self.shapes.reversed_list():
            if isinstance(shape, MultiSelectionShape) and multi_select:
                continue
            p = point
            if shape.is_within(p):
                return shape
        return None

    def draw(self, ctx):
        ctx.save()
        self.document_area_box.pre_draw(ctx)
        self.document_area_box.draw_path(ctx)
        self.document_area_box.draw_fill(ctx)

        ctx.save()
        self.multi_shape.draw(ctx)
        ctx.restore()
        self.multi_shape.draw_axis(ctx)

        if self.shape_editor:
            if isinstance(self.shape_editor.shape, MultiSelectionShape):
                self.shape_editor.shape.draw(ctx)
            self.shape_editor.draw(ctx)

        if self.shape_creator:
            self.shape_creator.draw(ctx)

        if False:
            ctx.save()
            self.multi_shape.pre_draw(ctx)
            Shape.rounded_rectangle(ctx, 0, 0, self.multi_shape.width, self.multi_shape.height, 2)
            #self.multi_shape.draw_border(ctx)
            draw_stroke(ctx, 1, "33333333")
            ctx.restore()
        #ctx.restore()

        #ctx.save()
        #self.document_area_box.pre_draw(ctx)
        self.document_area_box.draw_path(ctx)
        #self.document_area_box.draw_anchor(ctx)
        self.document_area_box.draw_border(ctx)
        ctx.restore()

        for guide in self.guides:
            ctx.save()
            guide.draw(ctx, self.out_width, self.out_height)
            ctx.restore()
        #ctx.restore()

    def zoom(self, scale, point, out_width, out_height):
        scale = 1. + scale*.1

        self.document_area_box.scale_x *= scale
        self.document_area_box.scale_y *= scale

        new_anchor_at = self.document_area_box.transform_point(point)
        new_anchor_at.scale(scale, scale)
        self.document_area_box.anchor_at.copy_from(new_anchor_at)

        self.document_area_box.move_to(point.x, point.y)
        self.resize_scollable_area(out_width, out_height)

    def scroll(self, value , direction, out_width, out_height):
        if direction == "vert":
            excess_height = self.scrollable_area.height - out_height
            pixel_value = value * excess_height
            self.document_area_box.translation.y = self.scrollable_area.offset_y-pixel_value
        elif direction == "horiz":
            excess_width = self.scrollable_area.width - out_width
            pixel_value = value * excess_width
            self.document_area_box.translation.x = self.scrollable_area.offset_x-pixel_value

    def get_scroll_position(self, out_width, out_height):
        excess_height = self.scrollable_area.height - float(out_height)
        if excess_height>0:
            y_pos = (self.scrollable_area.offset_y-self.document_area_box.translation.y)/excess_height
        else:
            y_pos = 0.
        excess_width = self.scrollable_area.width - float(out_width)
        if excess_width>0:
            x_pos = (self.scrollable_area.offset_x-self.document_area_box.translation.x)/excess_width
        else:
            x_pos = 0.
        return x_pos, y_pos

    def resize_scollable_area(self, out_width, out_height):
        self.out_width = out_width
        self.out_height = out_height
        rect = self.document_area_box.get_abs_outline(0)
        extra_y = 0
        if rect.top+rect.height>out_height:
            if rect.top>0:
                self.scrollable_area.height = 2*rect.top+rect.height
                self.scrollable_area.offset_y = rect.top
            else:
                extra_y = 50
                self.scrollable_area.height = rect.height+2*extra_y
                self.scrollable_area.offset_y = extra_y
        elif rect.top>0:
            if out_height-(rect.top+rect.height)>rect.top:
                extra_y = out_height-(rect.top+rect.height)-rect.top
                self.scrollable_area.height = out_height+extra_y
                self.scrollable_area.offset_y = rect.top+extra_y
            else:
                extra_y = rect.top-(out_height-(rect.top+rect.height))
                self.scrollable_area.height = out_height+extra_y
                self.scrollable_area.offset_y = rect.top
        else:
            extra_y = out_height-(rect.top+rect.height)
            self.scrollable_area.height = out_height+2*extra_y
            self.scrollable_area.offset_y = extra_y

        if rect.left+rect.width>out_width:
            if rect.left>0:
                self.scrollable_area.width = 2*rect.left+rect.width
                self.scrollable_area.offset_x = rect.left
            else:
                extra_x = 50
                self.scrollable_area.width = rect.width+2*extra_y
                self.scrollable_area.offset_x = extra_x
        elif rect.left>0:
            if out_width-(rect.left+rect.width)>rect.left:
                extra_x = out_width-(rect.left+rect.width)-rect.left
                self.scrollable_area.width = out_width+extra_x
                self.scrollable_area.offset_x = rect.left+extra_x
            else:
                extra_x = rect.left-(out_width-(rect.left+rect.width))
                self.scrollable_area.width = out_width+extra_x
                self.scrollable_area.offset_x = rect.left

    def fit_area_in_size(self, out_width, out_height):
        self.out_width = out_width
        self.out_height = out_height
        self.document_area_box.top = (out_height-self.document_area_box.height)*.5
        self.scroll(.5, "vert", out_width, out_height)
        self.scroll(.5, "horiz", out_width, out_height)

    def start_creating_new_shape(self, shape_type, doc_point, shape_point):
        point = shape_point
        self.delete_shape_editor()
        if shape_type == "rect":
            self.shape_creator = RectangleShapeCreator(point)
        elif shape_type == "oval":
            self.shape_creator = OvalShapeCreator(point)
        elif shape_type == "curve":
            self.shape_creator = CurveShapeCreator.create_blank(point)
        elif shape_type == "polygon":
            self.shape_creator = PolygonShapeCreator(point)
        elif shape_type == "freehand":
            self.shape_creator = FreehandShapeCreator(point)
        else:
            filename = os.path.join(settings.PREDRAWN_SHAPE_FOLDER, shape_type)
            if os.path.exists(filename):
                document = Document(filename=filename)
                self.shape_creator = PredrawnShapeCreator(point, document)

        if self.shape_creator:
            self.shape_creator.set_relative_to(self.multi_shape)
            self.current_task = ShapeAddTask(self.doc, self.multi_shape)
            self.add_shape(self.shape_creator.get_shape())
            #task.save(self.doc, self.shape_creator.shape)
            self.shape_creator.begin_movement(point)

    def create_image_shape(self, filename):
        image_pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        if not image_pixbuf: return False
        w = float(image_pixbuf.get_width())
        h = float(image_pixbuf.get_height())
        scale = min(self.doc.width/w, self.doc.height/h)
        if scale < 1:
            w *= scale
            h *= scale
        shape = ImageShape(anchor_at=Point(w*.5, h*.5),
                   border_color="000000",
                   border_width=1, fill_color="cccccc",
                   width=w, height=h, corner_radius=2)
        shape.set_image_path(filename)
        self.place_shape_at_zero_position(shape)
        self.add_shape(shape)
        shape.set_stage_xy(Point(0, 0))
        self.multi_shape.readjust_sizes()
        return True

    def delete_shape_editor(self):
        if self.shape_editor is None: return
        if isinstance(self.shape_editor.shape, MultiSelectionShape) :
            self.shape_editor.shape.remove_all_shapes()
            self.remove_shape(self.shape_editor.shape)
        self.shape_editor = None

    def select_document_area_box(self):
        self.document_area_box_selected = True
        self.init_document_area_box = self.document_area_box.copy()

    def select_item_at(self, doc_point, shape_point, multi_select=False):
        if self.document_area_box_selected: return

        point = shape_point
        if self.shape_creator is not None:
            self.shape_creator.begin_movement(point)
            return

        if not EditingChoice.LOCK_GUIDES:
            for guide in self.guides:
                if guide.is_within(doc_point):
                    self.selected_guide = guide
                    self.selected_guide.save_position()
                    return

        if self.shape_editor is not None:
            self.shape_editor.select_item_at(point, multi_select)

        if self.shape_editor is None or \
                (self.shape_editor is not None and not self.shape_editor.has_selected_box()):
            shape = self.get_shape_at(point, multi_select)
            if shape is None:
                self.delete_shape_editor()
            elif self.shape_editor is None:
                self.shape_editor = ShapeEditor(shape)
            elif shape != self.shape_editor.shape:
                if multi_select:
                    if not isinstance(self.shape_editor.shape, MultiSelectionShape) :
                        old_shape = self.shape_editor.shape
                        multi_selection_shape = MultiSelectionShape()
                        multi_selection_shape.be_like_shape(old_shape)
                        self.place_shape_at_zero_position(multi_selection_shape)
                        if old_shape != shape:
                            multi_selection_shape.add_shape(old_shape)

                        self.add_shape(multi_selection_shape)
                        self.shape_editor = ShapeEditor(multi_selection_shape)
                    else:
                        multi_selection_shape = self.shape_editor.shape

                    if multi_selection_shape.shapes.contain(shape):
                        multi_selection_shape.remove_shape(shape)
                        if len(multi_selection_shape.shapes)==1:
                            shapes = multi_selection_shape.remove_all_shapes()
                            self.delete_shape_editor()
                            self.shape_editor = ShapeEditor(shapes[-1])
                    else:
                        multi_selection_shape.add_shape(shape)
                    multi_selection_shape.move_anchor_at_center()
                else:
                    self.delete_shape_editor()
                    self.shape_editor = ShapeEditor(shape)

        if self.shape_editor is None:
            if doc_point.x<0 or doc_point.x>self.document_area_box.width:
                if 0<=doc_point.y<=self.document_area_box.height:
                    self.selected_guide = VerticalGuide(doc_point.x, self.document_area_box)
                    self.guides.append(self.selected_guide)
            elif doc_point.y<0 or doc_point.y>self.document_area_box.height:
                if 0<=doc_point.x<=self.document_area_box.width:
                    self.selected_guide = HorizontalGuide(doc_point.y, self.document_area_box)
                    self.guides.append(self.selected_guide)

    def move_active_item(self, doc_start_point, doc_end_point, shape_start_point, shape_end_point):
        if self.document_area_box_selected:
            dpoint = doc_end_point.diff(doc_start_point)
            abs_anchor_at = self.init_document_area_box.get_abs_anchor_at()
            abs_anchor_at.translate(dpoint.x, dpoint.y)
            self.document_area_box.move_to(abs_anchor_at.x, abs_anchor_at.y)
            return

        if self.shape_creator is not None:
            if self.current_task is None:
                self.current_task = ShapeStateTask(self.doc, self.shape_creator.shape)
            self.shape_creator.do_movement(shape_start_point, shape_end_point)

        elif self.selected_guide is not None:
            dpoint = doc_end_point.diff(doc_start_point)
            self.selected_guide.move(dpoint)

        elif self.shape_editor is not None:
            if self.current_task is None:
                self.current_task = ShapeStateTask(self.doc, self.shape_editor.shape)
            self.shape_editor.move_active_item(shape_start_point, shape_end_point)

    def end_movement(self):
        self.allow_mouse_move = False
        self.document_area_box_selected = False

        if self.shape_creator is not None:
            if self.current_task:
                self.current_task.save(self.doc, self.shape_creator.shape)
                self.current_task = None
            if self.shape_creator.end_movement():
                self.multi_shape.readjust_sizes()
                self.shape_creator = None

        elif self.selected_guide is not None:
            self.selected_guide.save_position()
            remove_guide = False
            if isinstance(self.selected_guide, VerticalGuide):
                if self.selected_guide.x<0 or self.selected_guide.x>self.document_area_box.width:
                    remove_guide = True
            if isinstance(self.selected_guide, HorizontalGuide):
                if self.selected_guide.y<0 or self.selected_guide.y>self.document_area_box.height:
                    remove_guide = True
            if remove_guide:
                self.guides.remove(self.selected_guide)
            self.selected_guide = None

        elif self.shape_editor is not None:
            self.multi_shape.readjust_sizes()
            self.shape_editor.end_movement()
            if self.current_task:
                self.current_task.save(self.doc, self.shape_editor.shape)
                self.current_task = None

    def complete_shape_creation(self):
        if self.shape_creator is not None:
            self.shape_creator.close_down()
            self.multi_shape.readjust_sizes()
            self.shape_creator = None

    def update(self):
        self.multi_shape.readjust_sizes()

    def combine_shapes(self):
        if not self.shape_editor:
            return

        new_shape = MultiShape()
        self.place_shape_at_zero_position(new_shape)
        if  isinstance(self.shape_editor.shape, MultiSelectionShape):
            multi_select_shape = self.shape_editor.shape
            new_shape.be_like_shape(multi_select_shape)

            while len(multi_select_shape.shapes)>0:
                child_shape = multi_select_shape.remove_shape(multi_select_shape.shapes.get_at_index(0))
                self.remove_shape(child_shape)
                new_shape.add_shape(child_shape)
            self.delete_shape_editor()
        else:
            child_shape = self.shape_editor.shape
            new_shape.be_like_shape(child_shape)

            self.remove_shape(child_shape)
            new_shape.add_shape(child_shape)

        new_shape._name = Shape.new_name()
        self.add_shape(new_shape)
        self.shape_editor = ShapeEditor(new_shape)

    def delete_selected_shape(self):
        if not self.shape_editor: return
        if not isinstance(self.shape_editor.shape, MultiSelectionShape):
            shape = self.shape_editor.shape
            task = ShapeDeleteTask(self.doc, shape)
            self.delete_shape_editor()
            self.remove_shape(shape)
            task.save(self.doc, self.multi_shape)

    def insert_point_in_shape_at(self, point):
        if not self.selected_shape_supports_point_insert(): return False
        shape = self.shape_editor.shape
        point = shape.transform_point(point)
        task = ShapeStateTask(self.doc, shape)
        if shape.insert_point_at(point):
            task.save(self.doc, shape)
            self.shape_editor = ShapeEditor(shape)
        else:
            task.remove(self.doc)

    def insert_break(self):
        if not self.shape_editor: return False
        if self.shape_editor.insert_break():
            self.shape_editor = ShapeEditor(self.shape_editor.shape)
            return True
        return False

    def join_points(self):
        if not self.shape_editor: return False
        if self.shape_editor.join_points():
            self.shape_editor = ShapeEditor(self.shape_editor.shape)
            return True
        return False

    def delete_point(self):
        if not self.shape_editor: return False
        if self.shape_editor.delete_point():
            self.shape_editor = ShapeEditor(self.shape_editor.shape)
            self.multi_shape.readjust_sizes()
            return True
        return False

    def extend_point(self):
        if not self.shape_editor: return False
        if self.shape_editor.extend_point():
            self.shape_editor = ShapeEditor(self.shape_editor.shape)
            self.multi_shape.readjust_sizes()
            return True
        return False

    def duplicate_shape(self):
        if not self.shape_editor: return False
        exist_shape = self.shape_editor.shape
        if isinstance(exist_shape, MultiShape):
            new_shape = exist_shape.copy(copy_shapes=True)
        else:
            new_shape = exist_shape.copy()
        self.add_shape(new_shape)
        self.shape_editor.shape.copy_into(new_shape)
        self.multi_shape.readjust_sizes()

        self.shape_editor = ShapeEditor(new_shape)
        return True

    def align_shapes(self, x_dir, y_dir):
        if not self.has_multi_selection(): return False
        multi_selection_shape = self.shape_editor.shape
        xy = None
        for shape in multi_selection_shape.shapes:
            if xy is None:
                xy = shape.get_stage_xy()
            else:
                if x_dir and not y_dir:
                    shape.set_stage_x(xy.x)
                elif not x_dir and y_dir:
                    shape.set_stage_y(xy.y)
                elif x_dir and y_dir:
                    shape.set_stage_xy(xy)

        multi_selection_shape.readjust_sizes()
        self.multi_shape.readjust_sizes()

    def convert_shape_to(self, shape_type):
        if not self.shape_editor: return False
        new_shape = None
        if shape_type == "polygon":
            if isinstance(self.shape_editor.shape, RectangleShape):
                new_shape = PolygonShape.create_from_rectangle_shape(self.shape_editor.shape)
        elif shape_type == "curve":
            if isinstance(self.shape_editor.shape, OvalShape):
                new_shape = CurveShape.create_from_oval_shape(self.shape_editor.shape)
        if new_shape:
            self.add_shape(new_shape)
            self.shape_editor.shape.copy_into(new_shape)
            self.remove_shape(self.shape_editor.shape)
            self.multi_shape.readjust_sizes()
            self.shape_editor = ShapeEditor(new_shape)
            return True
        return False
