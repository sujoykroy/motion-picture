import os

import json
from collections import OrderedDict

import tkinter as tk
from tkinter import filedialog

from app_config import AppConfig
from project_db import ProjectDb

from commons import Point, Rectangle
from ui_tk import CanvasImage
from slides import TextSlide, ImageSlide

THIS_DIR = os.path.abspath(__file__)

class Application(tk.Frame):
    MODE_CROP_CREATE = 1
    MODE_CROP_MOVE = 2
    MODE_CROP_RESIZE = 3

    def __init__(self, master=None, config_filename="app.ini"):
        super(Application, self).__init__(master=master)
        self.app_config = AppConfig(os.path.join(THIS_DIR, config_filename))
        self.active_slide_index = -1

        self.init_mouse_pos = Point()
        self.current_mouse_pos = Point()
        self.image_offset = Point()

        self.crop_mode = None
        self.crop_rect = None
        self.corner_rect = None
        self.movable_rect = None

        self.pack()

        #prompt for project filename
        project_filename = ""
        """
        project_filename= filedialog.asksaveasfilename(
                                    filetypes=[("JSON", "*.json")])
        """
        self.db = ProjectDb(project_filename)

        #image_dir = filedialog.askdirectory()
        image_dir = "/home/sujoy/Pictures/Zenfone"
        self.db.add_image_files_from_dir(image_dir)

        self.create_editing_widgets()
        self.show_slide()

    def create_editing_widgets(self,
                                canvas_width=400, canvas_border=2):
        canvas_height = canvas_width/self.app_config.aspect_ratio
        self.canvas_size = Point(canvas_width, canvas_height)
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height)
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_left_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_left_mouse_release)
        self.canvas.bind("<B1-Motion>", self.on_canvas_left_mouse_move)

        self.canvas_background = self.canvas.create_rectangle(
            canvas_border, canvas_border,
            canvas_width-canvas_border, canvas_height-canvas_border,
            fill="white", width=canvas_border)

        self.prev_button = tk.Button(
                    self, text="<<Prev", command=lambda: self.show_slide(-1))
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(
            self, text="Next>>", command=self.show_slide)
        self.next_button.pack(side=tk.LEFT)

    def show_slide(self, rel=1):
        slide_index =  self.active_slide_index + rel
        if slide_index<0:
            slide_index += self.db.slide_count
        slide_index %= self.db.slide_count

        self.active_slide = self.db.get_slide_at_index(slide_index)
        self.active_slide_index = slide_index

        self.slide_image = CanvasImage(self.active_slide.get_image(), self.canvas_size)
        self.image_offset.copy_from(self.slide_image.offset)
        self.canvas.image = self.canvas.create_image(
                self.slide_image.offset.x, self.slide_image.offset.y,
                image=self.slide_image.tk_image, anchor="nw")

    def on_canvas_left_mouse_press(self, event):
        self.init_mouse_pos.assign(event.x, event.y)
        self.movable_rect =None

        if not self.crop_rect:
            self.crop_mode = self.MODE_CROP_CREATE
            pos = self.init_mouse_pos

            self.crop_rect = Rectangle(pos.x, pos.y, pos.x, pos.y)
            self.corner_rect = Rectangle()

            self.canvas.crop_rect = self.canvas.create_rectangle(0, 0, 0, 0)
            self.canvas.corner_rect = self.canvas.create_rectangle(0, 0, 0, 0)
        elif self.corner_rect and self.corner_rect.is_within(self.init_mouse_pos):
            self.crop_mode = self.MODE_CROP_RESIZE
            self.movable_rect = self.corner_rect
        elif self.crop_rect.is_within(self.init_mouse_pos):
            self.crop_mode = self.MODE_CROP_MOVE
            self.movable_rect = self.crop_rect
        else:
            self.crop_mode == None

        if self.movable_rect:
            self.init_movable_rect = self.movable_rect.copy()
        self.update_canvas_rects()

    def on_canvas_left_mouse_move(self, event):
        self.current_mouse_pos.assign(event.x, event.y)
        if not self.crop_mode:
            return
        if self.crop_mode == self.MODE_CROP_CREATE:
            self.crop_rect.set_values(x2=self.current_mouse_pos.x, y2=self.current_mouse_pos.y)
            self.crop_rect.keep_x2y2_inside_bound(self.slide_image.bound_rect)
        else:
            diff_point = self.current_mouse_pos.diff(self.init_mouse_pos)

            rect = self.init_movable_rect.copy()
            rect.translate(diff_point)
            self.movable_rect.copy_from(rect)

            if self.crop_mode == self.MODE_CROP_RESIZE:
                self.crop_rect.set_values(
                        x2=self.corner_rect.get_cx(), y2=self.corner_rect.get_cy())
                self.crop_rect.keep_x2y2_inside_bound(self.slide_image.bound_rect)
            elif self.crop_mode == self.MODE_CROP_MOVE:
                self.crop_rect.keep_x1y1_inside_bound(self.slide_image.bound_rect)
        self.update_canvas_rects()

    def on_canvas_left_mouse_release(self, event):
        self.movable_rect = None

    def update_canvas_rects(self):
        self.crop_rect.adjust_to_aspect_ratio(self.app_config.aspect_ratio)
        self.corner_rect.set_cxy_wh(cx=self.crop_rect.x2,
                                    cy=self.crop_rect.y2, w=5, h=5)
        self.set_canvas_rect(self.canvas.crop_rect, self.crop_rect)
        self.set_canvas_rect(self.canvas.corner_rect, self.corner_rect)

    def set_canvas_rect(self, canvas_rect, rect):
        self.canvas.coords(canvas_rect, rect.x1, rect.y1, rect.x2, rect.y2)

tk_root = tk.Tk()
tk_root.title("Img2Vid")

app = Application(master=tk_root)
app.mainloop()
