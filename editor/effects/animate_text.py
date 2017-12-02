from MotionPicture.commons import draw_stroke, draw_fill, Point, Polygon, Color, draw_oval
from MotionPicture import TextShape

class Drawer(object):
    def __init__(self):
        self.params = dict()
        self.params_info = dict(
            text_shape_name=dict(type="text", default=""),
            path_shape_name=dict(type="text", default=""),
            motion_offset=dict(type="number", default=0, step_increment=.01, digits=2),
        )
        self.use_custom_surface = False

    def set_params(self, params):
        self.params.update(params)

    def set_progress(self, value):
        self.progress = value

    def draw(self, ctx, anchor_at, width, height, parent_shape):
        text_shape_name = self.params.get("text_shape_name")
        if isinstance(text_shape_name, str):
            text_shape_name = text_shape_name.decode("utf-8")
        orig_text_shape = parent_shape.get_interior_shape(text_shape_name)
        if not orig_text_shape:
            return

        path_shape_name = self.params.get("path_shape_name")
        if isinstance(path_shape_name, str):
            path_shape_name = path_shape_name.decode("utf-8")
        path_shape = parent_shape.get_interior_shape(path_shape_name)

        letter_rects = orig_text_shape.get_letter_positions(orig_text_shape.text, rel_to_anchor=True)
        text_shape = orig_text_shape.copy()
        text_shape.anchor_at = Point(0, 0)
        text_shape.max_width_chars = -1
        text_shape.x_align = 1
        text_shape.y_align = 0
        text_shape.border_width = 0
        text_shape.parent_shape = None
        text_shape.translation.assign(0, 0)
        text_shape.max_width_chars = 1
        text_shape.use_text_surface = False

        ctx.translate(anchor_at.x, anchor_at.y)
        if path_shape:
            spoint, sangle = path_shape.get_baked_point(1)

        progress_step = 1./len(letter_rects)
        motion_offset = self.params.get("motion_offset")
        for i in range(len(letter_rects)):
            offset_progress = i*progress_step-motion_offset
            progress = (self.progress-offset_progress)/(progress_step+motion_offset)
            if progress>1:
                progress = 1
            if progress<0:
                continue

            letter_rect = letter_rects[i]
            text = orig_text_shape.text[i]
            text_shape.width=letter_rect.width
            text_shape.height=letter_rect.height
            text_shape.display_text=text

            if path_shape:
                epoint, eangle = path_shape.get_baked_point(progress)
                epoint.translate(-spoint.x, -spoint.y)
                letter_rect.left += epoint.x
                letter_rect.top += epoint.y
            else:
                letter_rect.left = -anchor_at.x + (letter_rect.left+anchor_at.x)*progress
                letter_rect.top = -anchor_at.y + (letter_rect.top+anchor_at.y)*progress

            ctx.save()
            text_shape.move_to(letter_rect.left, letter_rect.top)
            text_shape.pre_draw(ctx)
            text_shape.draw_text(ctx, exclude_extents=False)
            text_shape.draw_path(ctx)
            ctx.restore()

        text_shape.cleanup()
