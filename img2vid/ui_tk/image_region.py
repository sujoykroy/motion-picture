from types import SimpleNamespace
from enum import Enum

from ..geom import Rectangle, Point

class RegionBox:
    LineColor = "#000000"

    def __init__(self, width, height, canvas):
        self.area = Rectangle(0, 0, width, height)
        self.widgets = SimpleNamespace(rect=None)
        self.canvas = canvas
        self.options = SimpleNamespace(
            fill_color=None, line_color=self.LineColor,
            line_width=1, hove_color=None)

    @property
    def left_top(self):
        return Point(self.area.x1, self.area.x2)

    def rebuild(self):
        self.clear()
        self.widgets.rect = self.canvas.create_rectangle(
            0, 0, 0, 0,
            outline=self.options.line_color,
            fill=self.options.fill_color,
            width=self.options.line_width)

    def clear(self):
        if not self.widgets.rect:
            return
        self.canvas.delete(self.widgets.rect)
        self.widgets.rect = None

    def redraw(self):
        if not self.widgets.rect:
            self.rebuild()
        self.canvas.coords(
            self.widgets.rect,
            self.area.x1, self.area.y1,
            self.area.x2, self.area.y2)

    def set_right_top(self, right, top, fixed_size=True):
        if fixed_size:
            self.area.set_values(
                x1=right-self.area.width,
                y1=top,
                x2=right,
                y2=top+self.area.height)
        else:
            self.area.set_values(y1=top, x2=right)
        self.redraw()

    def set_right_bottom(self, right, bottom, fixed_size=True):
        if fixed_size:
            self.area.set_values(
                x1=right-self.area.width,
                y1=bottom-self.area.height,
                x2=right,
                y2=bottom)
        else:
            self.area.set_values(x2=right, y2=bottom)
        self.redraw()

    def set_left_top(self, left, top, fixed_size=True):
        if fixed_size:
            self.area.set_values(
                x1=left,
                y1=top,
                x2=left+self.area.width,
                y2=top+self.area.height)
        else:
            self.area.set_values(x1=left, y1=top)
        self.redraw()

class CrossBox(RegionBox):
    FillColor = "#FF0000"

    def __init__(self, width, height, canvas):
        super().__init__(width, height, canvas)
        self.widgets.line_1 = None
        self.widgets.line_2 = None
        self.options.fill_color = self.FillColor

    def rebuild(self):
        super().rebuild()
        self.widgets.line_1 = self.canvas.create_line(
            0, 0, 0, 0, fill=self.options.line_color)
        self.widgets.line_2 = self.canvas.create_line(
            0, 0, 0, 0, fill=self.options.line_color)

    def clear(self):
        super().clear()
        if self.widgets.line_1:
            self.canvas.delete(self.widgets.line_1)
            self.widgets.line_1 = None
        if self.widgets.line_2:
            self.canvas.delete(self.widgets.line_2)
            self.widgets.line_2 = None

    def redraw(self):
        super().redraw()
        self.canvas.coords(
            self.widgets.line_1,
            self.area.x1, self.area.y1,
            self.area.x2, self.area.y2)
        self.canvas.coords(
            self.widgets.line_2,
            self.area.x1, self.area.y2,
            self.area.x2, self.area.y1)

class OuterBox(RegionBox):
    LineColor2 = "#FFFFFF"

    def __init__(self, width, height, canvas):
        super().__init__(width, height, canvas)
        self.options.line_color2 = self.LineColor2
        self.widgets.rect2 = None

    def rebuild(self):
        super().rebuild()
        self.widgets.rect2 = self.canvas.create_rectangle(
            0, 0, 0, 0,
            outline=self.options.line_color2,
            fill=self.options.fill_color,
            width=self.options.line_width)

    def clear(self):
        super().clear()
        if self.widgets.rect2:
            self.canvas.delete(self.widgets.rect2)
            self.widgets.rect2 = None

    def redraw(self):
        super().redraw()
        self.canvas.coords(
            self.widgets.rect2,
            self.area.x1-self.options.line_width,
            self.area.y1-self.options.line_width,
            self.area.x2+self.options.line_width,
            self.area.y2+self.options.line_width)

class ImageRegion:
    AspectRatio = 16/9
    CrossSize = 10
    HookSize = 10
    HookFillColor = "#0cae80"

    _IdSeed = 0

    def __init__(self, canvas):
        self._canvas = canvas
        self.outer_box = OuterBox(0, 0, canvas)
        self.outer_box.rebuild()

        self.cross_box = CrossBox(
            self.CrossSize, self.CrossSize, canvas)

        self.hook_box = RegionBox(
            self.HookSize, self.HookSize, canvas)
        self.hook_box.options.fill_color = self.HookFillColor

        self._selected = False
        self._id_num = self._IdSeed + 1
        ImageRegion._IdSeed += 1

    @property
    def left_top(self):
        return Point(self.outer_box.area.x1, self.outer_box.area.y1)

    @property
    def selected(self):
        return self._selected

    @property
    def id_num(self):
        return self._id_num

    def __eq__(self, other):
        return isinstance(other, ImageRegion) and self.id_num == other.id_num

    @selected.setter
    def selected(self, value):
        self._selected = value
        if self._selected:
            self.cross_box.rebuild()
            self.hook_box.rebuild()
            self._readjust()
        else:
            self.cross_box.clear()
            self.hook_box.clear()

    def clear(self):
        self.outer_box.clear()
        self.cross_box.clear()
        self.hook_box.clear()

    def set_right_bottom(self, right, bottom, bound_rect):
        left_top = self.outer_box.left_top
        if right-left_top.x < 2*self.CrossSize:
            right = left_top.x + 2*self.CrossSize
        if  bottom-left_top.y < 2*self.CrossSize:
            bottom = left_top.y + 2*self.CrossSize

        self.outer_box.set_right_bottom(right, bottom, fixed_size=False)
        self.outer_box.area.adjust_to_aspect_ratio(self.AspectRatio)
        self.outer_box.area.keep_x2y2_inside_bound(bound_rect)
        self.outer_box.redraw()
        self._readjust()

    def set_left_top(self, left, top, bound_rect, fixed_size=False):
        self.outer_box.set_left_top(left, top, fixed_size=fixed_size)
        self.outer_box.area.keep_x1y1_inside_bound(bound_rect)
        self.outer_box.area.keep_x2y2_inside_bound(bound_rect)
        self.outer_box.redraw()
        self._readjust()

    def is_within_outer(self, point):
        return self.outer_box.area.is_within(point)

    def is_within_cross(self, point):
        return self.cross_box.area.is_within(point)

    def is_within_hook(self, point):
        return self.hook_box.area.is_within(point)

    def _readjust(self):
        if not self._selected:
            return
        self.cross_box.set_right_top(
            right=self.outer_box.area.x2,
            top=self.outer_box.area.y1)
        self.hook_box.set_right_bottom(
            right=self.outer_box.area.x2,
            bottom=self.outer_box.area.y2)

class RegionMode(Enum):
    NONE = 0
    RESIZE = 1
    MOVE = 2
    DELETE = 3

class ImageRegionManager:
    SelectionColor = "#ddea07"
    SelectionPadding = 1

    def __init__(self, canvas):
        self._canvas = canvas
        self._mode = RegionMode.NONE

        self._regions = []
        self._selected_region = None

        self._init_region_pos = Point(0, 0)
        self._bound_rect = Rectangle(0, 0, 0, 0)
        self._selection_box = RegionBox(0, 0, canvas)
        self._selection_box.options.line_color = self.SelectionColor
        self._selection_box.options.line_width = self.SelectionPadding+1

    @property
    def bound_rect(self):
        return self._bound_rect.copy()

    @bound_rect.setter
    def bound_rect(self, rect):
        self._bound_rect.copy_from(rect)

    @property
    def should_delete_region(self):
        return self._selected_region and self._mode == RegionMode.DELETE

    def clear(self):
        self._selected_region = None
        self._selection_box.clear()
        for region in self._regions:
            region.clear()
        del self._regions[:]

    def get_region_rects(self):
        rects = []
        for region in self._regions:
            rects.append(region.outer_box.area.copy())
        return rects

    def create_region_at(self, point):
        if not self._bound_rect.is_within(point):
            return
        region = ImageRegion(self._canvas)
        region.set_left_top(
            left=point.x, top=point.y,
            bound_rect=self._bound_rect,
            fixed_size=True)
        self._regions.append(region)
        self._set_selected_region(region)
        self._mode = RegionMode.RESIZE

    def remove_selected(self):
        if self._selected_region:
            self._regions.remove(self._selected_region)
            self._selected_region.clear()
        self._set_selected_region(None)

    def select_item_at(self, point):
        if not self._bound_rect.is_within(point):
            self._set_selected_region(None)
            return None

        selected_region = self._selected_region
        if self._selected_region:
            if self._selected_region.is_within_hook(point):
                self._mode = RegionMode.RESIZE
            elif self._selected_region.is_within_cross(point):
                self._mode = RegionMode.DELETE
            elif self._selected_region.is_within_outer(point):
                self._mode = RegionMode.MOVE
            else:
                self._mode = RegionMode.NONE
                selected_region = None

        if not selected_region:
            for region in self._regions:
                if region.is_within_outer(point):
                    selected_region = region
                    self._mode = RegionMode.MOVE
                    break

        self._set_selected_region(selected_region)
        self._update_selection_box()
        return self._selected_region

    def move_item(self, start_point, end_point):
        if not self._selected_region:
            return
        if not self._bound_rect.is_within(end_point):
            end_point = end_point.copy()
            end_point.x = min(end_point.x, self._bound_rect.x2)
            end_point.x = max(end_point.x, self._bound_rect.x1)

            end_point.y = min(end_point.y, self._bound_rect.y2)
            end_point.y = max(end_point.y, self._bound_rect.y1)

        diff_point = end_point.diff(start_point)
        if self._mode == RegionMode.RESIZE:
            self._selected_region.set_right_bottom(
                end_point.x, end_point.y, self._bound_rect)
        elif self._mode == RegionMode.MOVE:
            left = self._init_region_pos.x + diff_point.x
            top = self._init_region_pos.y + diff_point.y
            self._selected_region.set_left_top(
                left, top, self._bound_rect, fixed_size=True)
        self._update_selection_box()

    def _set_selected_region(self, region):
        if self._selected_region:
            self._selected_region.selected = False
        self._selected_region = region
        if region:
            region.selected = True
            self._init_region_pos.copy_from(region.left_top)
        self._update_selection_box()

    def _update_selection_box(self):
        if self._selected_region:
            rect = self._selected_region.outer_box.area
            self._selection_box.area.set_values(
                x1=rect.x1-self.SelectionPadding,
                y1=rect.y1-self.SelectionPadding,
                x2=rect.x2+self.SelectionPadding,
                y2=rect.y2+self.SelectionPadding)
            self._selection_box.redraw()
        else:
            self._selection_box.clear()
