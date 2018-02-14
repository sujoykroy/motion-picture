from types import SimpleNamespace
import tkinter as tk
import PIL.ImageTk

from ..geom import Point, Rectangle
from .frame import Frame
from ..slides import TextSlide, ImageSlide
from ..renderer import ImageRenderer
from .image_region import ImageRegionManager

class ImageFitter:
    def __init__(self):
        self.render_info = None
        self.canvas_size = Point(0, 0)

        self.rects = SimpleNamespace()
        self.rects.image = Rectangle(0, 0, 0, 0)
        self.rects.screen = Rectangle(0, 0, 0, 0)
        self.rects.editable = Rectangle(0, 0, 0, 0)

        self.orig_image_scale = 1
        self.image_tk = None

    def build_screen_area(self, width, height, screen_config):
        self.canvas_size.assign(width, height)

        scale = min(
            width/screen_config.width, height/screen_config.height)
        if scale == 0:
            self.rects.screen.set_values(0, 0, 0, 0)
            return
        screen_width = int(screen_config.width*scale)
        screen_height = int(screen_config.height*scale)

        screen_left = int((width-screen_width)*0.5)
        screen_top = int((height-screen_height)*0.5)

        self.rects.screen.set_values(
            x1=screen_left,
            y1=screen_top,
            x2=screen_left+screen_width,
            y2=screen_top+screen_height)
        self.fit()

    def fit(self):
        if not self.render_info:
            return
        if self.canvas_size.x == 0:
            return

        image = self.render_info.image
        width = self.rects.screen.width
        height = int(image.height*width/image.width)

        if height > self.rects.screen.height:
            height = self.rects.screen.height
            width = int(image.width*height/image.height)

        self.orig_image_scale = width/image.width
        self.rects.editable.copy_from(self.render_info.editable_rect)
        self.rects.editable.same_scale(self.orig_image_scale)

        image = ImageRenderer.resize(image, width, height)
        left = int((self.canvas_size.x-width)*0.5)
        top = int((self.canvas_size.y-height)*0.5)

        self.rects.image.set_values(
            x1=left, y1=top,
            x2=left+width, y2=top+height)

        self.rects.editable.translate(
            Point(self.rects.image.x1, self.rects.image.y1))
        self.image_tk = PIL.ImageTk.PhotoImage(image=image)

    def reverse_transform_rect(self, rect):
        rect.translate(
            Point(self.rects.editable.x1, self.rects.editable.y1), sign=-1)
        rect.same_scale(1/self.orig_image_scale)
        return rect

class ImageEditor(Frame):
    def __init__(self, master, app_config):
        super().__init__(
            master=master,
            app_config=app_config)

        self._slide = None
        self._fitter = ImageFitter()
        self._mouse_pos = SimpleNamespace(start=Point(0, 0), end=Point(0, 0))

        canvas = tk.Canvas(master=self.base,
                highlightbackground=self.app_config.editor_back_color)
        self.widgets.canvas = canvas
        canvas.pack(fill=tk.BOTH, expand=1)
        canvas.slide_image = None
        canvas.back_image_tk = None
        canvas.back_image = None

        canvas.bind("<ButtonPress-1>", self._on_left_mouse_press)
        canvas.bind("<ButtonRelease-1>", self._on_left_mouse_release)
        canvas.bind("<B1-Motion>", self._on_left_mouse_move)
        canvas.bind("<Configure>", self._on_resize)

        canvas.background = canvas.create_rectangle(
            0, 0, 0, 0,
            fill=self.app_config.editor_back_color, width=0)

        self._region_manager = ImageRegionManager(canvas)

    def get_region_rects(self):
        rects = self._region_manager.get_region_rects()
        for rect in rects:
            self._fitter.reverse_transform_rect(rect)
        return rects

    def set_slide(self, slide):
        same_slide = (self._slide == slide)
        self._slide = slide

        if isinstance(slide, TextSlide):
            render_info = ImageRenderer.build_text_slide(
                slide,
                self.app_config.video_render,
                self.app_config.text)
        elif isinstance(slide, ImageSlide):
            render_info = ImageRenderer.build_image_slide(
                slide,
                self.app_config.video_render,
                self.app_config.image)
        else:
            render_info = None
        self._fitter.render_info = render_info
        self._fitter.fit()
        self._update_region_manager()

        if not same_slide:
            self._clear_slide()
            self._region_manager.clear()
        self._redraw_slide()

    def _update_region_manager(self):
        self._region_manager.bound_rect = self._fitter.rects.editable

    def _clear_slide(self):
        canvas = self.widgets.canvas
        if canvas.slide_image:
            canvas.delete(canvas.slide_image)
            canvas.slide_image = None

    def _redraw_slide(self):
        canvas = self.widgets.canvas
        if not self._fitter.image_tk and \
           not canvas.slide_image:
            return

        if not canvas.slide_image:
            canvas.slide_image = canvas.create_image(
                self._fitter.rects.image.x1,
                self._fitter.rects.image.y1,
                image=self._fitter.image_tk,
                anchor=tk.N+tk.W)
        else:
            canvas.itemconfig(canvas.slide_image, image=self._fitter.image_tk)
            canvas.coords(
                canvas.slide_image,
                self._fitter.rects.image.x1,
                self._fitter.rects.image.y1)

    def _on_left_mouse_press(self, event):
        if not self._slide or not self._slide.crop_allowed:
            return
        self._mouse_pos.start.assign(event.x, event.y)
        self._mouse_pos.end.assign(event.x, event.y)

        if not self._region_manager.select_item_at(self._mouse_pos.start):
            self._region_manager.create_region_at(self._mouse_pos.start)

    def _on_left_mouse_move(self, event):
        if not self._slide or not self._slide.crop_allowed:
            return
        self._mouse_pos.end.assign(event.x, event.y)
        self._region_manager.move_item(
            self._mouse_pos.start, self._mouse_pos.end)

    def _on_left_mouse_release(self, _event):
        if not self._slide or not self._slide.crop_allowed:
            return
        if self._region_manager.should_delete_region:
            self._region_manager.remove_selected()

    def _on_resize(self, _event):
        canvas = self.widgets.canvas
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        self._fitter.build_screen_area(width, height, self.app_config.video_render)
        self._update_region_manager()
        canvas.coords(canvas.background, 0, 0, width, height)

        canvas.back_image_tk = PIL.ImageTk.PhotoImage(
            image=ImageRenderer.create_blank(
                self._fitter.rects.screen.width,
                self._fitter.rects.screen.height,
                self.app_config.video_render.back_color
            )
        )
        if not canvas.back_image:
            canvas.back_image = canvas.create_image(
                self._fitter.rects.screen.x1,
                self._fitter.rects.screen.y1,
                image=canvas.back_image_tk,
                anchor=tk.N+tk.W)
        else:
            canvas.itemconfig(
                canvas.back_image,
                image=canvas.back_image_tk)
            canvas.coords(
                canvas.back_image,
                self._fitter.rects.screen.x1,
                self._fitter.rects.screen.y1)
        self._redraw_slide()
