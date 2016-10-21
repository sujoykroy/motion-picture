from gi.repository import GdkPixbuf
import os

from shape_editor import ShapeEditor
from gradient_color_editor import GradientColorEditor

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
        doc.main_multi_shape.parent_shape = self.document_area_box

        self.shape_hierarchy = [multi_shape]
        last_shape = multi_shape
        while last_shape.parent_shape and last_shape.parent_shape != self.document_area_box:
            last_shape = last_shape.parent_shape
            self.shape_hierarchy.insert(0, last_shape)

        self.last_doc_point = None
        self.last_shape_point = None

        self.selection_box = RectangleShape(Point(0, 0), border_color="00000066", border_width=2,
                                            fill_color=None, width=1., height=1., corner_radius=0.)
        self.selection_box.parent_shape = self.multi_shape
        self.selection_box.visible = False
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
        self.color_editor = None
        self.eraser_box = None


    def create_eraser(self, size=5.):
        if not (self.shape_editor and \
                isinstance(self.shape_editor.shape, CurveShape)):
            return False
        self.eraser_box = OvalShape(Point(size*.5, size*.5),
                border_color="000000", border_width=1, fill_color="ffffff",
                width=size, height=size, sweep_angle=360)
        self.eraser_box.parent_shape = self.multi_shape
        return True

    def delete_eraser(self):
        self.eraser_box = None

    def reload_shapes(self):
        self.delete_shape_editor()
        self.shape_creator = None
        self.shapes = ShapeList(self.multi_shape.shapes)

    def get_doc_point(self, point):
        return self.document_area_box.transform_point(point)

    def get_shape_point(self, doc_point):
        point = doc_point.copy()
        for multi_shape in self.shape_hierarchy:
            point = multi_shape.transform_point(point)
        return point

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

    def copy_selected_shapes(self):
        if not self.shape_editor: return None
        shapes = []
        if isinstance(self.shape_editor.shape, MultiSelectionShape):
            for shape in self.shape_editor.shape.shapes:
                shapes.append(shape.copy(deep_copy=True))
        else:
            shapes.append(self.shape_editor.shape.copy(deep_copy=True))
        return shapes

    def add_shape(self, shape):
        if not isinstance(shape, MultiSelectionShape):
            self.multi_shape.add_shape(shape)
        shape.parent_shape = self.multi_shape
        self.shapes.add(shape)

    def remove_shape(self, shape):
        self.shapes.remove(shape)
        self.multi_shape.remove_shape(shape)

    def rename_shape(self, shape, name):
        old_name = shape.get_name()
        if self.multi_shape.rename_shape(shape, name):
            return self.shapes.rename(old_name, name)
        return False

    def get_shape_at(self, point, multi_select):
        for shape in self.shapes.reversed_list():
            if isinstance(shape, MultiSelectionShape) and multi_select:
                continue
            if isinstance(shape.parent_shape, MultiSelectionShape) and multi_select:
                continue
            p = point
            if shape.is_within(p):
                return shape
        return None

    def draw(self, ctx, drawing_size):
        set_default_line_style(ctx)

        ctx.save()
        self.document_area_box.pre_draw(ctx)
        self.document_area_box.draw_path(ctx)
        self.document_area_box.draw_fill(ctx)
        ctx.restore()
        self.document_area_box.draw_axis(ctx)

        ctx.save()
        self.multi_shape.draw(ctx, drawing_size)
        ctx.restore()
        if not EditingChoice.HIDE_AXIS:
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
            self.multi_shape.draw_border(ctx)
            draw_stroke(ctx, 1, "000000")
            ctx.restore()

        ctx.save()
        self.document_area_box.pre_draw(ctx)
        self.document_area_box.draw_path(ctx)
        #self.document_area_box.draw_anchor(ctx)
        self.document_area_box.draw_border(ctx)
        ctx.restore()

        if self.eraser_box:
            ctx.save()
            self.eraser_box.draw(ctx)
            ctx.restore()

        if self.selection_box.visible:
            ctx.save()
            #self.multi_shape.pre_draw(ctx)
            self.selection_box.pre_draw(ctx)
            self.selection_box.draw_path(ctx)
            ctx.restore()
            self.selection_box.draw_border(ctx)
        #ctx.restore()

        if self.color_editor:
            self.color_editor.draw(ctx)

        for guide in self.guides:
            ctx.save()
            guide.draw(ctx, self.out_width, self.out_height)
            ctx.restore()

    def zoom(self, scale, point, out_width, out_height):
        scale = 1. + scale*.1

        new_anchor_at = self.document_area_box.transform_point(point)
        #new_anchor_at.scale(scale, scale)
        self.document_area_box.anchor_at.copy_from(new_anchor_at)

        self.document_area_box.scale_x *= scale
        self.document_area_box.scale_y *= scale
        self.document_area_box.move_to(point.x, point.y)

        self.resize_scollable_area(out_width, out_height)
        self.document_area_box.anchor_at.assign(self.doc.width*.5, self.doc.height*.5)

    def get_scale(self):
        return self.document_area_box.scale_x

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
        scale = min(out_width/self.doc.width, out_height/self.doc.height)
        self.document_area_box.scale_x = scale
        self.document_area_box.scale_y = scale
        self.document_area_box.move_to(out_width*.5, out_height*.5)

        self.resize_scollable_area(out_width, out_height)
        self.scroll(.5, "vert", out_width, out_height)
        self.scroll(.5, "horiz", out_width, out_height)

    def start_creating_new_shape(self, shape_type, doc_point, shape_point):
        point = shape_point
        if shape_type == "rect":
            self.shape_creator = RectangleShapeCreator(point)
        elif shape_type == "oval":
            self.shape_creator = OvalShapeCreator(point)
        elif shape_type == "curve":
            self.shape_creator = CurveShapeCreator.create_blank(point)
        elif shape_type == "polygon":
            self.shape_creator = PolygonShapeCreator(point)
        elif shape_type == "freehand":
            if self.shape_editor and isinstance(self.shape_editor.shape, CurveShape):
                curve_shape = self.shape_editor.shape
            else:
                curve_shape = None
            self.shape_creator = FreehandShapeCreator(point, curve_shape=curve_shape)
        elif shape_type == "ring":
            self.shape_creator = RingShapeCreator(point)
        elif shape_type == "text":
            self.shape_creator = TextShapeCreator(point)
        else:
            filename = os.path.join(settings.PREDRAWN_SHAPE_FOLDER, shape_type)
            if os.path.exists(filename):
                document = Document(filename=filename)
                self.shape_creator = PredrawnShapeCreator(point, document)

        self.delete_shape_editor()
        if self.shape_creator:
            self.last_doc_point = doc_point.copy()
            #self.place_shape_at_zero_position(self.shape_creator.shape)
            self.shape_creator.set_relative_to(self.multi_shape)
            if not self.multi_shape.shapes.contain(self.shape_creator.get_shape()):
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
        self.color_editor = None

    def select_document_area_box(self):
        self.document_area_box_selected = True
        self.init_document_area_box = self.document_area_box.copy()

    def select_item_at(self, mouse_point, multi_select=False, box_select=False):
        if self.document_area_box_selected: return

        doc_point = self.get_doc_point(mouse_point)
        if self.shape_creator is not None:
            if EditingChoice.LOCK_XY_MOVEMENT :
                if EditingChoice.LOCK_XY_GLOBAL:
                    if self.last_doc_point:
                        if EditingChoice.LOCK_XY_MOVEMENT == "y":
                            doc_point.x = self.last_doc_point.x
                        elif EditingChoice.LOCK_XY_MOVEMENT == "x":
                            doc_point.y = self.last_doc_point.y
                        self.last_doc_point.x = doc_point.x
                        self.last_doc_point.y = doc_point.y
                    else:
                        self.last_doc_point = doc_point.copy()
                    shape_point = self.get_shape_point(doc_point)
            else:
                shape_point = self.get_shape_point(doc_point)
            self.shape_creator.begin_movement(shape_point)
            return

        shape_point = self.get_shape_point(doc_point)

        if box_select:
            self.selection_box.visible = True
            self.selection_box.set_width(1.)
            self.selection_box.set_height(1.)
            self.selection_box.move_to(shape_point.x, shape_point.y)
            return

        if not EditingChoice.LOCK_GUIDES:
            for guide in self.guides:
                if guide.is_within(doc_point):
                    self.selected_guide = guide
                    self.selected_guide.save_position()
                    return

        if self.color_editor is not None:
            self.color_editor.select_item_at(shape_point)
            if self.color_editor.selected_edit_box:
                return

        if EditingChoice.FREE_ERASING:
            if self.eraser_box is None:
                self.create_eraser()
            if self.eraser_box is not None:
                #point = self.shape_editor.shape.transform_point(shape_point)
                self.eraser_box.move_to(shape_point.x, shape_point.y)
                return

        if self.shape_editor is not None:
            self.shape_editor.select_item_at(shape_point, multi_select)

        if self.shape_editor is None or \
                (self.shape_editor is not None and not self.shape_editor.has_selected_box()):
            shape = self.get_shape_at(shape_point, multi_select)
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

    def move_active_item(self, mouse_start_point, mouse_end_point):
        doc_start_point = self.get_doc_point(mouse_start_point)
        doc_end_point = self.get_doc_point(mouse_end_point)

        if self.selection_box.visible:
            shape_start_point = self.get_shape_point(doc_start_point)
            shape_end_point = self.get_shape_point(doc_end_point)

            drel_point = shape_end_point.diff(shape_start_point)
            if drel_point.x<0:
                move_x = shape_end_point.x
            else:
                move_x = shape_start_point.x
            if drel_point.y<0:
                move_y = shape_end_point.y
            else:
                move_y = shape_start_point.y
            self.selection_box.set_width(abs(drel_point.x))
            self.selection_box.set_height(abs(drel_point.y))
            self.selection_box.move_to(move_x, move_y)
            return

        if EditingChoice.LOCK_XY_MOVEMENT :
            if EditingChoice.LOCK_XY_GLOBAL:
                if self.last_doc_point:
                    if EditingChoice.LOCK_XY_MOVEMENT == "y":
                        doc_start_point.x = self.last_doc_point.x
                        doc_end_point.x = self.last_doc_point.x
                    elif EditingChoice.LOCK_XY_MOVEMENT == "x":
                        doc_start_point.y = self.last_doc_point.y
                        doc_end_point.y = self.last_doc_point.y
                else:
                    if EditingChoice.LOCK_XY_MOVEMENT == "y":
                        doc_end_point.x = doc_start_point.x
                    elif EditingChoice.LOCK_XY_MOVEMENT == "x":
                        doc_end_point.y = doc_start_point.y
                shape_start_point = self.get_shape_point(doc_start_point)
                shape_end_point = self.get_shape_point(doc_end_point)
        else:
            shape_start_point = self.get_shape_point(doc_start_point)
            shape_end_point = self.get_shape_point(doc_end_point)

        if self.last_doc_point:
            self.last_doc_point.x = doc_end_point.x
            self.last_doc_point.y = doc_end_point.y
        else:
            self.last_doc_point = doc_end_point.copy()

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

        elif self.color_editor and self.color_editor.selected_edit_box:
            self.color_editor.move_active_item(shape_start_point, shape_end_point)
        elif self.shape_editor is not None:
            if self.current_task is None:
                self.current_task = ShapeStateTask(self.doc, self.shape_editor.shape)
            if self.eraser_box is not None:
                shape = self.shape_editor.shape
                self.eraser_box.move_to(shape_end_point.x, shape_end_point.y)
                res = shape.delete_dest_points_inside_rect(
                    shape_end_point, self.eraser_box.width
                )
                if res and shape.show_points:
                    self.delete_shape_editor()
                    self.shape_editor = ShapeEditor(shape)
            else:
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

        else:
            if self.selection_box.visible:
                selection_rect = self.selection_box.get_abs_outline(0)
                self.selection_box.visible = False

                if self.shape_editor is None or \
                    not self.shape_editor.select_items_inside_rect(selection_rect):
                    selected_shapes = []
                    for shape in self.shapes:
                        if isinstance(shape, MultiSelectionShape): continue
                        if shape.is_inside_rect(selection_rect):
                            selected_shapes.append(shape)
                    if selected_shapes:
                        self.delete_shape_editor()
                        if len(selected_shapes)>1:
                            multi_selection_shape = MultiSelectionShape()
                            for shape in selected_shapes:
                                multi_selection_shape.add_shape(shape)
                            selected_shape = multi_selection_shape
                            self.add_shape(multi_selection_shape)
                        else:
                            selected_shape = selected_shapes[0]
                        self.shape_editor = ShapeEditor(selected_shape)
            elif self.color_editor:
                self.color_editor.end_movement()
            elif self.shape_editor is not None:
                if self.eraser_box:
                    self.delete_eraser()
                else:
                    self.multi_shape.readjust_sizes()
                    self.shape_editor.end_movement()
                if self.current_task:
                    self.current_task.save(self.doc, self.shape_editor.shape)
                    self.current_task = None

    def complete_shape_creation(self):
        if self.shape_creator is not None:
            self.shape_creator.close_down()
            if self.current_task:
                self.current_task.save(self.doc, self.shape_creator.shape)
                self.current_task = None
            #if isinstance(self.shape_creator, FreehandShapeCreator):
                #task = ShapeStateTask(self.doc, self.shape_creator.shape)
                #for curve in self.shape_creator.shape.curves:
                #    curve.smoothe_out(self._shape_creation_task_start, self._shape_creation_task_end)
                #task.save(self.doc, self.shape_creator.shape)
            self.multi_shape.readjust_sizes()
            self.shape_creator = None

    def shape_editor_task_start(self):
        return ShapeStateTask(self.doc, self.shape_editor.shape)

    def shape_editor_task_end(self, task):
        task.save(self.doc, self.shape_editor.shape)

    def update(self):
        self.multi_shape.readjust_sizes()

    def combine_shapes(self):
        if not self.shape_editor:
            return
        task = ShapeCombineTask(self.doc, self.shape_editor.shape)
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
        task.save(self.doc, new_shape)

    def delete_selected_shape(self):
        if not self.shape_editor: return None
        if self.doc.main_multi_shape != self.multi_shape and \
           len(self.multi_shape.shapes) == 1: return None
        if not isinstance(self.shape_editor.shape, MultiSelectionShape):
            shape = self.shape_editor.shape
            task = ShapeDeleteTask(self.doc, shape)
            self.delete_shape_editor()
            self.remove_shape(shape)
            shape.cleanup()
            task.save(self.doc, self.multi_shape)
            return shape
        return None

    def insert_point_in_shape_at(self, point):
        if not self.selected_shape_supports_point_insert(): return False
        shape = self.shape_editor.shape
        point = shape.transform_point(point)
        task = ShapeStateTask(self.doc, self.shape_editor.shape)
        if shape.insert_point_at(point):
            task.save(self.doc, shape)
            self.shape_editor = ShapeEditor(shape)
        else:
            task.remove(self.doc)

    def double_click_in_color_editor(self, point):
        if not self.color_editor: return False
        self.color_editor.select_item_at(point)
        shape = self.color_editor.parent_shape
        task = ShapeStateTask(self.doc, shape)
        if self.color_editor.selected_edit_box:
            self.color_editor.choose_color()
        else:
            self.color_editor.insert_point_at(point)
        task.save(self.doc, shape)

    def insert_break(self):
        if not self.shape_editor: return False
        task = ShapeStateTask(self.doc, self.shape_editor.shape)
        if self.shape_editor.insert_break():
            task.save(self.doc, self.shape_editor.shape)
            self.shape_editor = ShapeEditor(self.shape_editor.shape)
            return True
        else:
            task.remove(self.doc)
        return False

    def join_points(self):
        if not self.shape_editor: return False
        task = ShapeStateTask(self.doc, self.shape_editor.shape)
        if self.shape_editor.join_points():
            task.save(self.doc, self.shape_editor.shape)
            self.shape_editor = ShapeEditor(self.shape_editor.shape)
            return True
        else:
            task.remove(self.doc)
        return False

    def delete_point(self):
        if not self.shape_editor: return False
        task = ShapeStateTask(self.doc, self.shape_editor.shape)
        if self.shape_editor.delete_point():
            task.save(self.doc, self.shape_editor.shape)
            self.shape_editor = ShapeEditor(self.shape_editor.shape)
            self.multi_shape.readjust_sizes()
            return True
        else:
            task.remove(self.doc)
        return False

    def extend_point(self):
        if not self.shape_editor: return False
        task = ShapeStateTask(self.doc, self.shape_editor.shape)
        if self.shape_editor.extend_point():
            task.save(self.doc, self.shape_editor.shape)
            self.shape_editor = ShapeEditor(self.shape_editor.shape)
            self.multi_shape.readjust_sizes()
            return True
        else:
            task.remove(self.doc)
        return False

    def duplicate_shape(self, linked=False):
        if not self.shape_editor: return False
        exist_shape = self.shape_editor.shape
        new_shapes = []
        old_shapes = []

        if isinstance(exist_shape, MultiSelectionShape):
            for old_shape in exist_shape.shapes:
                old_shapes.append(old_shape)
            self.delete_shape_editor()

            for old_shape in old_shapes:
                if isinstance(old_shape, MultiShape):
                    new_shapes.append(old_shape.copy(copy_shapes=True, deep_copy=True))
                else:
                    new_shapes.append(old_shape.copy(deep_copy=True))
        elif isinstance(exist_shape, MultiShape):
            old_shapes.append(exist_shape)
            new_shapes.append(exist_shape.copy(copy_shapes=True, deep_copy=True))
        else:
            old_shapes.append(exist_shape)
            new_shapes.append(exist_shape.copy(deep_copy=True))

        self.delete_shape_editor()

        for i in range(len(new_shapes)):
            new_shape = new_shapes[i]
            old_shape = old_shapes[i]
            self.add_shape(new_shape)
            old_shape.copy_into(new_shape)
            if linked and (isinstance(new_shape, PolygonShape) or \
                           isinstance(new_shape, CurveShape) or \
                           isinstance(new_shape, MultiShape)):
                new_shape.set_linked_to(exist_shape)

        self.multi_shape.readjust_sizes()

        if len(new_shapes)>1:
            multi_selection_shape = MultiSelectionShape()
            for new_shape in new_shapes:
                multi_selection_shape.add_shape(new_shape)
            self.add_shape(multi_selection_shape)
            self.shape_editor = ShapeEditor(multi_selection_shape)
        elif new_shapes:
            self.shape_editor = ShapeEditor(new_shapes[0])

        return True

    def align_shapes(self, x_dir, y_dir):
        if not self.shape_editor: return False

        task = ShapeStateTask(self.doc, self.shape_editor.shape)
        if isinstance(self.shape_editor.shape, MultiSelectionShape):
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
        elif isinstance(self.shape_editor.shape, PolygonShape) or \
             isinstance(self.shape_editor.shape, CurveShape):
            self.shape_editor.align_points(x_dir, y_dir)
        task.save(self.doc, self.shape_editor.shape)
        return True

    def convert_shape_to(self, shape_type):
        if not self.shape_editor: return False
        new_shape = None
        old_shape = self.shape_editor.shape
        if shape_type == "polygon":
            if isinstance(old_shape, RectangleShape) and old_shape.corner_radius == 0:
                new_shape = PolygonShape.create_from_rectangle_shape(old_shape)
        elif shape_type == "curve":
            if isinstance(old_shape, RectangleShape) and old_shape.corner_radius > 0:
                new_shape = CurveShape.create_from_rectangle_shape(old_shape)
            elif isinstance(old_shape, OvalShape):
                new_shape = CurveShape.create_from_oval_shape(old_shape)
            elif isinstance(old_shape, PolygonShape):
                new_shape = CurveShape.create_from_polygon_shape(old_shape)
        if new_shape:
            task = ShapeConvertTask(self.doc, self.shape_editor.shape)
            self.add_shape(new_shape)
            old_shape.copy_into(new_shape)
            self.remove_shape(old_shape)

            new_shape_name = new_shape.get_name()
            self.multi_shape.shapes.rename(new_shape_name, old_shape.get_name())
            self.shapes.rename(new_shape_name, old_shape.get_name())

            self.multi_shape.readjust_sizes()
            self.reload_shapes()
            self.shape_editor = ShapeEditor(new_shape)
            task.save(self.doc, new_shape)
            return True
        return False

    def change_shape_depth(self, depth_offset):
        if not self.shape_editor: return False
        if isinstance(self.shape_editor.shape, MultiSelectionShape): return False
        self.multi_shape.shapes.change_index(self.shape_editor.shape.get_name(), depth_offset)
        self.shapes.change_index(self.shape_editor.shape.get_name(), depth_offset)
        return True

    def merge_shapes(self):
        if not self.shape_editor: return False
        if not isinstance(self.shape_editor.shape, MultiSelectionShape): return False
        mega_shape = None
        merged_shapes = []

        flat_merge = False
        for shape in self.shape_editor.shape.shapes:
            if isinstance(shape, MultiShape):
                flat_merge = True
                mega_shape = shape

        for shape in self.shape_editor.shape.shapes:
            if flat_merge:
                if shape == mega_shape: continue
            else:
                if not isinstance(shape, PolygonShape) and \
                    not isinstance(shape, CurveShape):
                    continue
            if mega_shape is None:
                mega_shape = shape
                continue
            elif not flat_merge and not isinstance(shape, type(mega_shape)):
                continue
            if flat_merge or mega_shape.include_inside(shape):
                merged_shapes.append(shape)

        if merged_shapes:
            task = ShapeMergeTask(self.doc, self.shape_editor.shape, merged_shapes)
            self.delete_shape_editor()
            newly_added_shapes = []
            for shape in merged_shapes:
                if flat_merge:
                    new_shape = shape.copy()
                    shape.copy_into(new_shape, all_fields=True)
                    mega_shape.add_shape(new_shape)
                    newly_added_shapes.append(new_shape)
                self.remove_shape(shape)
            self.shape_editor = ShapeEditor(mega_shape)
            task.save(self.doc, mega_shape, newly_added_shapes)
            return True

        return False

    def break_selected_multi_shape(self):
        if not self.shape_editor: return False
        shape = self.shape_editor.shape
        if isinstance(shape, MultiSelectionShape): return False
        if not isinstance(shape, MultiShape): return False
        task = MultiShapeBreakTask(self.doc, shape)
        freed_shapes = []
        for child_shape_name in list(shape.shapes.names):
            child_shape = shape.shapes[child_shape_name]
            shape.remove_shape(child_shape)
            child_shape.recreate_name()
            self.multi_shape.add_shape(child_shape, transform=False, resize=False)
            freed_shapes.append(child_shape)
        self.remove_shape(shape)
        self.multi_shape.readjust_sizes()
        task.save(self.doc, self.multi_shape)
        self.reload_shapes()
        return True

    def save_doc(self, filename=None):
        shapes = []
        if self.shape_editor and isinstance(self.shape_editor.shape, MultiSelectionShape):
            for shape in self.shape_editor.shape.shapes:
                shapes.append(shape)
            self.delete_shape_editor()

        self.doc.save(filename)
        if shapes:
            multi_selection_shape = MultiSelectionShape()
            for shape in shapes:
                multi_selection_shape.add_shape(shape)
            self.add_shape(multi_selection_shape)
            self.shape_editor = ShapeEditor(multi_selection_shape)

    def update_linked_shapes(self):
        if not self.shape_editor: return False
        selected_shapes = []

        if isinstance(self.shape_editor.shape, MultiSelectionShape):
            for shape in self.shape_editor.shape.shapes:
                selected_shapes.append(shape)
        else:
            selected_shapes.append(self.shape_editor.shape)

        for selected_shape in selected_shapes:
            if selected_shape.linked_to:
                selected_shape.copy_data_from_linked()
            if selected_shape.linked_clones:
                for linked_clone in selected_shape.linked_clones:
                    if linked_clone in selected_shapes:
                        continue
                    linked_clone.copy_data_from_linked()
        return True

    def place_anchor_at_center_of_shape(self):
        if not self.shape_editor: return False
        shape = self.shape_editor.shape
        if not isinstance(shape, MultiSelectionShape):
            task = ShapeStateTask(self.doc, shape)

        shape.anchor_at.x = shape.width*.5
        shape.anchor_at.y = shape.height*.5

        if not isinstance(shape, MultiSelectionShape):
            task.save(self.doc, shape)
        return True

    def toggle_color_editor(self, prop_name, color_type):
        if self.color_editor:
            self.color_editor = None
            return
        if not self.shape_editor: return
        shape = self.shape_editor.shape
        self.color_editor = GradientColorEditor(prop_name, shape)
