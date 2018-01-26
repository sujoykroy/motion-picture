import os

import json
from collections import OrderedDict

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.scrolledtext as tkscrolledtext

from project_db import ProjectDb

from commons import Point, Rectangle, AppConfig
from ui_tk import CanvasImage, PreviewPlayer
from slides import TextSlide, ImageSlide, VideoFrameMaker

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

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

        self.db = None
        self.crop_mode = None
        self.crop_rect = None
        self.corner_rect = None
        self.movable_rect = None

        self.active_slide = None
        self.slide_image = None
        self.preview_player = None

        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.pack(expand=True, fill=tk.BOTH)

        self.init_frame = tk.Frame(self)
        self.init_frame.pack()
        self.create_button = tk.Button(
                        self.init_frame, text="Create New Project",
                        command=self.on_create_project_button_clicked, default=tk.ACTIVE)
        self.create_button.pack(side=tk.LEFT, padx=5, pady=5, expand=1, fill=tk.X)

        self.open_button = tk.Button(
                        self.init_frame, text="Open Existing Project",
                        command=self.on_open_project_button_clicked, default=tk.ACTIVE)
        self.open_button.pack(side=tk.RIGHT, padx=5, pady=5, expand=1, fill=tk.X)

    def create_editing_widgets(self, canvas_width=400):
        self.container_frame = tk.Frame(self)
        self.container_frame.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        self.container_frame.columnconfigure(1, weight=1)
        self.container_frame.rowconfigure(0, weight=1)


        canvas_height = canvas_width/self.app_config.aspect_ratio
        self.canvas = tk.Canvas(self.container_frame,
                            width=canvas_width, height=canvas_height, highlightbackground="black")
        self.canvas.grid(row=0, column=0, columnspan=5, sticky=tk.N+tk.S+tk.W+tk.E)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_left_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_left_mouse_release)
        self.canvas.bind("<B1-Motion>", self.on_canvas_left_mouse_move)

        self.canvas.crop_rect = None
        self.canvas.corner_rect = None
        self.canvas.image = None
        self.canvas.text = None

        self.canvas_active_area = Rectangle(0, 0, canvas_width, canvas_height)
        self.canvas_background = self.canvas.create_rectangle(
            0, 0, canvas_width, canvas_height, fill="white", width=0)

        self.prev_button = tk.Button(self.container_frame,
                                     text="<<Prev", command=lambda: self.show_slide(-1))
        self.prev_button.grid(row=1, column=0, sticky=tk.W)

        self.slide_info_label = tk.Label(self.container_frame, text="0/0")
        self.slide_info_label.grid(row=1, column=1)

        self.next_button = tk.Button(self.container_frame,
                                     text="Next>>", command=self.show_slide)
        self.next_button.grid(row=1, column=2, sticky=tk.W)

        self.preview_button = tk.Button(self.container_frame,
                                     text="Preview", command=self.on_preview_button_click)
        self.preview_button.grid(row=1, column=3, sticky=tk.E)

        self.add_text_button = tk.Button(self.container_frame,
                                     text="Add Text Slide", command=self.add_text_slide)
        self.add_text_button.grid(row=1, column=4, sticky=tk.E)

        self.slide_tool_frame = tk.Frame(self)
        self.slide_tool_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.caption_label = tk.Label(self.slide_tool_frame, text="Caption")
        self.caption_label.pack()

        self.caption_text = tkscrolledtext.ScrolledText(
                        self.slide_tool_frame, height="5", width="40")
        self.caption_text.pack()
        self.caption_text.bind("<KeyRelease>", self.on_key_in_caption_text)

        self.align_label = tk.Label(self.slide_tool_frame, text="Alignment")
        self.align_label.pack()

        self.text_align_options =  ["top", "bottom", "center"]
        self.text_alignlist = tk.Listbox(self.slide_tool_frame, height=5)
        for item in self.text_align_options:
            self.text_alignlist.insert(tk.END, item)
        self.text_alignlist.bind("<ButtonRelease-1>", self.on_text_alignment_select)
        self.text_alignlist.pack()

        self.crop_button = tk.Button(self.slide_tool_frame,
                                     text="Crop", command=self.crop_image_slide)
        self.crop_button.pack(side=tk.BOTTOM)

        self.delete_slide_button = tk.Button(self.slide_tool_frame,
                                     text="Delete Slide", command=self.delete_slide)
        self.delete_slide_button.pack(side=tk.BOTTOM)

        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def set_states_of_image_options(self, state):
        for item in [self.align_label, self.text_alignlist, self.crop_button]:
            item["state"] = state
        if state == "normal":
            self.caption_label["text"] = "Caption"
        else:
            self.caption_label["text"] = "Text"

    def clear_slide_display(self):
        if self.canvas.crop_rect:
            self.canvas.delete(self.canvas.crop_rect)
        if self.canvas.corner_rect:
            self.canvas.delete(self.canvas.corner_rect)
        if self.canvas.image:
            self.canvas.delete(self.canvas.image)
        if self.canvas.text:
            self.canvas.delete(self.canvas.text)

        self.canvas.crop_rect = None
        self.canvas.corner_rect = None
        self.canvas.image = None
        self.canvas.text = None

        self.crop_rect = None
        self.corner_rect = None
        self.slide_image = None
        self.crop_mode = None

        self.text_alignlist.selection_clear(0, tk.END)
        self.caption_text.delete("1.0", tk.END)
        self.set_states_of_image_options("disable")
        self.canvas.itemconfig(self.canvas_background, fill="white")

    def show_slide(self, rel=1):
        self.clear_slide_display()

        slide_index =  self.active_slide_index + rel
        if slide_index<0:
            slide_index += self.db.slide_count
        slide_index %= self.db.slide_count

        self.active_slide = self.db.get_slide_at_index(slide_index)
        self.active_slide_index = slide_index

        self.slide_info_label["text"] = "{0}/{1}".format(slide_index+1, self.db.slide_count)

        if self.active_slide.TypeName == ImageSlide.TypeName:
            self.set_states_of_image_options("normal")

            self.slide_image = CanvasImage(self.active_slide.get_image(), self.canvas_active_area)
            self.canvas.image = self.canvas.create_image(
                    self.slide_image.offset.x, self.slide_image.offset.y,
                    image=self.slide_image.tk_image, anchor="nw")
            self.caption_text.insert(tk.END, self.active_slide.get_caption())
            align = self.active_slide.get_caption_alignment()
            self.text_alignlist.selection_set(self.text_align_options.index(align))

        elif self.active_slide.TypeName == TextSlide.TypeName:
            self.canvas.itemconfig(self.canvas_background, fill=self.app_config.text_background_color)

            self.canvas.text = self.canvas.create_text(
                self.canvas_active_area.get_cx(),
                self.canvas_active_area.get_cy(),
                text=self.active_slide.get_text(),
                fill=self.app_config.text_foreground_color,
                font = self.app_config.get_font_tuple(),
                justify="center")
            self.caption_text.insert(tk.END, self.active_slide.get_text())

    def crop_image_slide(self):
        if not self.active_slide or self.active_slide.allow_cropping:
            return
        if not self.crop_rect or self.crop_rect.get_width()<10:
            return
        rect = self.slide_image.canvas2image(self.crop_rect)
        new_image_slide = self.active_slide.crop(rect)
        self.db.add_slide(new_image_slide, after=self.active_slide_index)
        self.show_slide(1)

    def add_text_slide(self):
        text_slide = TextSlide(text="Put text here")
        self.db.add_slide(text_slide, before=self.active_slide_index)
        self.show_slide(0)

    def delete_slide(self):
        if messagebox.askyesno("Delete Slide", "Do you really want to delete this slide?"):
            self.db.remove_slide(self.active_slide_index)
            self.active_slide_index = min(self.active_slide_index, self.db.slide_count-1)
            self.show_slide(0)

    def open_or_create_file(self, open=True):
        filetypes = [("JSON", "*.json")]
        if open:
            project_filename= filedialog.askopenfilename(filetypes=filetypes)
        else:
            project_filename= filedialog.asksaveasfilename(filetypes=filetypes)
        if not project_filename:
            self.master.destroy()
        return project_filename

    def on_create_project_button_clicked(self):
        project_filename= self.open_or_create_file(open=False)
        if not project_filename:
            return
        self.db = ProjectDb(project_filename)

        image_dir = filedialog.askdirectory()

        if not image_dir:
            self.master.destroy()
            return
        self.db.add_image_files_from_dir(image_dir)
        if not self.db.slide_count:
            self.master.destroy()
            return
        self.db.save()

        self.init_frame.destroy()
        self.create_editing_widgets()
        self.show_slide()

    def on_open_project_button_clicked(self):
        project_filename= self.open_or_create_file(open=True)
        if not project_filename:
            return
        self.db = ProjectDb(project_filename)

        self.init_frame.destroy()
        self.create_editing_widgets()
        self.show_slide()

    def on_preview_button_click(self):
        if self.preview_player:
            return
        self.video_frame_maker = VideoFrameMaker(self.db.slides, self.app_config)
        self.preview_player = PreviewPlayer(
            self, self.video_frame_maker, self.app_config, self.on_preview_window_close)
        self.preview_player.top.bind("WM_DELETE_WINDOW", self.on_preview_window_close)
        self.wait_window(self.preview_player.top)

    def on_text_alignment_select(self, event):
        sel = self.text_alignlist.curselection()
        if sel and sel[0]<len(self.text_align_options):
            align = self.text_align_options[sel[0]]
            self.active_slide.set_caption_alignment(align)

    def on_key_in_caption_text(self, event):
        if not self.active_slide:
            return
        text = self.caption_text.get(1.0, tk.END)
        if self.active_slide.TypeName == ImageSlide.TypeName:
            self.active_slide.set_caption(text)
        elif self.active_slide.TypeName == TextSlide.TypeName:
            self.active_slide.set_text(text)
            self.canvas.itemconfig(self.canvas.text, text=text)

    def on_canvas_left_mouse_press(self, event):
        if not self.slide_image:
            return
        self.init_mouse_pos.assign(event.x, event.y)
        self.movable_rect =None

        if not self.crop_rect:
            self.crop_mode = self.MODE_CROP_CREATE
            self.crop_button["state"] = "normal"
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
        if not self.slide_image:
            return
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
        if not self.slide_image:
            return
        self.movable_rect = None
        if self.crop_rect:
            self.crop_rect.standardize()
        self.update_canvas_rects()

    def on_canvas_resize(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.canvas_active_area.set_values(x2=canvas_width, y2=canvas_height)
        self.canvas.coords(self.canvas_background,
                    0, 0, canvas_width, canvas_height)
        self.show_slide(0)

    def on_preview_window_close(self):
        self.preview_player = None

    def on_window_close(self):
        if self.preview_player:
            self.preview_player.close()
        self.preview_player = None
        if self.db:
            self.db.save()
        self.master.destroy()

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

#place the window at the center of screen
tk_root.withdraw()
tk_root.update_idletasks()
x = (tk_root.winfo_screenwidth() - tk_root.winfo_reqwidth()) / 2
y = (tk_root.winfo_screenheight() - tk_root.winfo_reqheight()) / 2
tk_root.geometry("+%d+%d" % (x, y))
tk_root.deiconify()

app.mainloop()
