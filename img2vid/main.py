#!/usr/bin/env python3

import os
import json

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
import tkinter.scrolledtext as tkscrolledtext

from PIL import ImageTk
import imageio

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

#Pre Download FFMPEG
imageio.plugins.ffmpeg.download()

def show_tk_widget_at_center(tk_widget, use_req=False):
    tk_widget.withdraw()
    tk_widget.update_idletasks()
    if use_req:
        x = (tk_widget.winfo_screenwidth() - tk_widget.winfo_reqwidth()) / 2
        y = (tk_widget.winfo_screenheight() - tk_widget.winfo_reqheight()) / 2
    else:
        x = (tk_widget.winfo_screenwidth() - tk_widget.winfo_width()) / 2
        y = (tk_widget.winfo_screenheight() - tk_widget.winfo_height()) / 2
    tk_widget.geometry("+%d+%d" % (x, y))
    tk_widget.deiconify()
    tk_widget.update_idletasks()

class Application(tk.Frame):
    FRAME_MODE_CREATE_OPEN = 0
    FRAME_MODE_EDITING = 1

    MODE_CROP_CREATE = 1
    MODE_CROP_MOVE = 2
    MODE_CROP_RESIZE = 3

    def __init__(self, master=None, config_filename="app.ini", width=800, height=400):
        super(Application, self).__init__(master=master)
        self.app_config = AppConfig(os.path.join(THIS_DIR, config_filename))
        self.master.resize(width, height)

        self.text_align_options =  ["top", "bottom", "center"]
        self.active_slide_index = 0
        self.frame_mode = -1
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

        self.project_frame = None
        self.editing_frame = None

        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.pack(expand=True, fill=tk.BOTH)
        self.create_project_widgets()

    def create_project_widgets(self):
        self.frame_mode = self.FRAME_MODE_CREATE_OPEN
        self.project_frame = tk.Frame(self)
        self.project_frame.pack(expand=True, fill=tk.BOTH)
        self.create_project_button = tk.Button(
                        self.project_frame, text="Create New Project",
                        command=self.on_create_project_button_click)
        self.create_project_button.pack(padx=5, pady=5, fill=tk.BOTH, expand=1)

        self.open_project_button = tk.Button(
                        self.project_frame, text="Open Existing Project",
                        command=self.on_open_project_button_click, default=tk.ACTIVE)
        self.open_project_button.pack(padx=5, pady=5, fill=tk.BOTH, expand=1)

        self.quit_project_button = tk.Button(
                        self.project_frame, text="Quit",
                        command=self.on_quit_project_button_click)
        self.quit_project_button.pack(padx=5, pady=5, fill=tk.BOTH, expand=1)

        self.master.show_at_center()

    def destroy_project_widgets(self):
        if self.project_frame:
            self.project_frame.destroy()
        self.create_project_button = None
        self.open_project_button = None
        self.quit_project_button = None
        self.project_frame = None

    def create_editing_widgets(self, canvas_width=400):
        self.active_slide_index = 0
        self.frame_mode = self.FRAME_MODE_EDITING

        self.editing_frame = tk.Frame(self, relief=tk.RIDGE, borderwidth=1)
        self.editing_frame.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        self.editing_frame.columnconfigure(1, weight=1)
        self.editing_frame.rowconfigure(1, weight=1)

        canvas_height = canvas_width/self.app_config.aspect_ratio
        self.canvas = tk.Canvas(self.editing_frame,
                            width=canvas_width, height=canvas_height, highlightbackground="black")
        self.canvas.grid(row=1, column=0, columnspan=3, sticky=tk.N+tk.S+tk.W+tk.E)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_left_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_left_mouse_release)
        self.canvas.bind("<B1-Motion>", self.on_canvas_left_mouse_move)

        self.canvas.crop_rect = None
        self.canvas.corner_rect = None
        self.canvas.image = None
        self.canvas.text = None
        self.canvas.cap_img = None

        self.canvas_active_area = Rectangle(0, 0, canvas_width, canvas_height)
        self.canvas_background = self.canvas.create_rectangle(
            0, 0, canvas_width, canvas_height, fill="white", width=0)

        self.prev_button = tk.Button(self.editing_frame,
                                     text="<<Prev", command=lambda: self.show_slide(-1))
        self.prev_button.grid(row=2, column=0, sticky=tk.W)

        self.slide_info_label = tk.Label(self.editing_frame, text="0/0")
        self.slide_info_label.grid(row=2, column=1)

        self.next_button = tk.Button(self.editing_frame,
                                     text="Next>>", command=self.show_slide)
        self.next_button.grid(row=2, column=2, sticky=tk.W)

        self.slide_tool_frame = tk.Frame(self.editing_frame)
        self.slide_tool_frame.grid(row=1, column=3, rowspan=2, sticky=tk.N+tk.S)

        self.caption_label = tk.Label(self.slide_tool_frame, text="Caption")
        self.caption_label.pack()

        self.caption_text = tkscrolledtext.ScrolledText(
                        self.slide_tool_frame, height="5", width="40")
        self.caption_text.pack()
        self.caption_text.bind("<KeyRelease>", self.on_key_in_caption_text)

        self.align_label = tk.Label(self.slide_tool_frame, text="Alignment")
        self.align_label.pack()

        self.text_alignlist = tk.Listbox(self.slide_tool_frame, height=5)
        for item in self.text_align_options:
            self.text_alignlist.insert(tk.END, item)
        self.text_alignlist.bind("<ButtonRelease-1>", self.on_text_alignment_select)
        self.text_alignlist.pack()

        filter_types = Slide.get_filter_types()

        self.filter_frame = tk.Frame(self.slide_tool_frame)
        self.filter_frame.pack()

        self.filter_label = tk.Label(self.filter_frame, text="Filters")
        self.filter_label.pack(pady=5)

        self.filter_check_buttons = {}
        for filter_code in sorted(filter_types.keys()):
            filter_name = filter_types[filter_code]
            filter_var = tk.IntVar()

            filter_check_button = tk.Checkbutton(
                            self.filter_frame, text=filter_name,
                            variable=filter_var, command=self.on_filter_check_button_change)
            filter_check_button.pack(anchor=tk.W)
            filter_check_button.filter_var = filter_var
            filter_check_button.filter_code = filter_code
            self.filter_check_buttons[filter_code] = filter_check_button

        self.crop_button = tk.Button(self.slide_tool_frame,
                                     text="Crop", command=self.on_crop_image_slide_button_click)
        self.crop_button.pack(side=tk.BOTTOM)

        self.on_delete_slide_button_click_button = tk.Button(self.slide_tool_frame,
                                     text="Delete Slide", command=self.on_delete_slide_button_click)
        self.on_delete_slide_button_click_button.pack(side=tk.BOTTOM)


        self.bottom_packer = tk.Frame(self.editing_frame, relief=tk.GROOVE, borderwidth=1)
        self.bottom_packer.grid(row=0, column=0, columnspan=4, sticky=tk.E+tk.W)

        self.close_editing_button = tk.Button(self.bottom_packer,
                                     text="Close", command=self.on_close_editing_button_click)
        self.close_editing_button.pack(side=tk.RIGHT)

        self.preview_button = tk.Button(self.bottom_packer,
                                     text="Preview", command=self.on_preview_button_click)
        self.preview_button.pack(side=tk.RIGHT)

        self.add_text_button = tk.Button(self.bottom_packer,
                                     text="Add Text Slide", command=self.on_add_text_slide_button_click)
        self.add_text_button.pack(side=tk.LEFT)

        self.add_image_button = tk.Button(self.bottom_packer,
                                     text="Add Image Slide(s)", command=self.on_add_image_slide_button_click)
        self.add_image_button.pack(side=tk.LEFT)

        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.master.show_at_center()

    def destroy_editing_widgets(self):
        self.clear_slide_display()
        if self.db:
            self.db.save()
        if self.editing_frame:
            self.editing_frame.destroy()
            self.slide_tool_frame.destroy()

        self.canvas = None
        self.editing_frame  = None
        self.slide_tool_frame = None

        self.canvas_active_area = None
        self.canvas_background = None
        self.prev_button = None
        self.slide_info_label = None
        self.next_button = None
        self.preview_button = None
        self.add_text_button = None
        self.slide_tool_frame = None
        self.caption_label = None
        self.caption_text = None
        self.align_label = None
        self.text_alignlist = None
        self.crop_button = None
        self.filter_frame = None
        self.on_delete_slide_button_click_button = None
        for filter_check_button in self.filter_check_buttons.values():
            filter_check_button.destroy()
        self.fitler_check_buttons = None

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
            self.canvas.crop_rect = None
        if self.canvas.corner_rect:
            self.canvas.delete(self.canvas.corner_rect)
            self.canvas.corner_rect = None
        if self.canvas.image:
            self.canvas.delete(self.canvas.image)
            self.canvas.image = None
        if self.canvas.text:
            self.canvas.delete(self.canvas.text)
            self.canvas.text = None
        if self.canvas.cap_img:
            self.canvas.delete(self.canvas.cap_img)
            self.canvas.cap_img= None

        self.canvas.cap_img_image = None
        self.slide_image = None
        self.crop_mode = None
        self.crop_rect = None
        self.corner_rect = None

        self.text_alignlist.selection_clear(0, tk.END)
        self.caption_text.delete("1.0", tk.END)
        self.set_states_of_image_options("disable")
        self.canvas.itemconfig(self.canvas_background, fill=self.app_config.video_background_color)
        for filter_check_button in self.filter_check_buttons.values():
            filter_check_button.filter_var.set(0)

    def update_image_slide_on_canvas(self):
        image_area = self.canvas_active_area.copy()
        caption_metric = self.active_slide.get_caption_metric(self.app_config)
        if caption_metric:
            align = self.active_slide.get_caption_alignment()
            if align == "top":
                image_area.set_values(y1=image_area.y1+caption_metric.height*self.canvas.scale)
            elif align == "bottom":
                image_area.set_values(y2=image_area.y2-caption_metric.height*self.canvas.scale)

        self.slide_image.fit_inside(image_area)

        if caption_metric:
            caption_image = self.active_slide.get_caption_image(
                                self.slide_image.image.width/self.canvas.scale,
                                caption_metric, self.app_config, use_pil=True)
            caption_image = caption_image.resize(
                (int(caption_image.width*self.canvas.scale),
                 int(caption_image.height*self.canvas.scale)), resample=True)
            caption_size = Point(caption_image.width, caption_image.height)


        if not self.canvas.image:
            self.canvas.image = self.canvas.create_image(
                self.slide_image.offset.x, self.slide_image.offset.y,
                image=self.slide_image.tk_image, anchor=tk.N+tk.W)
        else:
            self.canvas.itemconfig(self.canvas.image, image=self.slide_image.tk_image)
            self.canvas.coords(self.canvas.image,
                               self.slide_image.offset.x, self.slide_image.offset.y)

        if caption_metric:
            self.canvas.cap_img_image = ImageTk.PhotoImage(image=caption_image)
            if not self.canvas.cap_img:
                self.canvas.cap_img = self.canvas.create_image(0,0, image=self.canvas.cap_img_image, fill=None)
            else:
                self.canvas.itemconfig(self.canvas.cap_img, image=self.canvas.cap_img_image)

            align = self.active_slide.get_caption_alignment()
            if align == "top":
                cap_x = self.canvas.winfo_width()*.5
                cap_y = self.slide_image.offset.y-caption_image.height*0.5
            elif align == "bottom":
                cap_x = self.canvas.winfo_width()*.5
                cap_y = self.slide_image.offset.y+self.slide_image.image.height+caption_image.height*0.5
            else:#center
                cap_x = self.canvas.winfo_width()*0.5
                cap_y = self.canvas.winfo_height()*0.5

            self.canvas.coords(self.canvas.cap_img, cap_x, cap_y)
        else:
            if self.canvas.cap_img:
                self.canvas.delete(self.canvas.cap_img)
                self.canvas.cap_img = None

    def update_text_slide_on_canvas(self):
        text_image = self.active_slide.get_renderable_image(self.app_config)
        text_image = text_image.resize(
            (int(text_image.width*self.canvas.scale),
             int(text_image.height*self.canvas.scale)), resample=True)
        self.text_img = ImageTk.PhotoImage(text_image)
        if not self.canvas.text:
            self.canvas.text = self.canvas.create_image(100, 0, image=self.text_img)
        else:
            self.canvas.itemconfig(self.canvas.text, image=self.text_img)
        self.canvas.coords(
            self.canvas.text,
            int(self.canvas.winfo_width()*0.5),
            int(self.canvas.winfo_height()*0.5))

    def show_slide(self, rel=1):
        self.clear_slide_display()
        if self.db.slide_count == 0:
            return

        slide_index =  self.active_slide_index + rel
        if slide_index<0:
            slide_index += self.db.slide_count
        slide_index %= self.db.slide_count

        self.active_slide = self.db.get_slide_at_index(slide_index)
        self.active_slide_index = slide_index

        self.slide_info_label["text"] = "{0}/{1}".format(slide_index+1, self.db.slide_count)
        for filter_code in self.active_slide.filters:
            self.filter_check_buttons[filter_code].filter_var.set(1)

        if self.active_slide.TypeName == ImageSlide.TypeName:
            self.set_states_of_image_options("normal")

            self.slide_image = CanvasImage(self.active_slide.get_image())
            self.update_image_slide_on_canvas()

            self.caption_text.insert(tk.END, self.active_slide.get_caption())
            align = self.active_slide.get_caption_alignment()
            self.text_alignlist.selection_set(self.text_align_options.index(align))

        elif self.active_slide.TypeName == TextSlide.TypeName:
            #self.canvas.itemconfig(self.canvas_background, fill=self.app_config.text_background_color)
            self.update_text_slide_on_canvas()
            self.caption_text.insert(tk.END, self.active_slide.get_text())
        self.canvas.update_idletasks()

    def open_or_create_file(self, open=True):
        filetypes = [("JSON", "*.json")]
        if open:
            project_filename= filedialog.askopenfilename(
                filetypes=filetypes, title="Select a project file to open")
        else:
            project_filename= filedialog.asksaveasfilename(
                filetypes=filetypes, title="Choose folder and write filename to save new project")
        if project_filename:
            root, ext = os.path.splitext(project_filename)
            if ext != ".json":
                project_filename += ".json"
        return project_filename

    def get_image_files_from_user(self):
        image_files = filedialog.askopenfilenames(
                title="Select images to import",
                filetypes=(("Images", self.app_config.get_image_types()),
                           ("All Files", "*.*")))
        return image_files

    def add_image_files(self, image_files, after_index=None):
        count = 0
        for filepath in image_files:
            root, ext = os.path.splitext(filepath)
            if ext.lower() in self.app_config.image_extensions:
                slide = ImageSlide(filepath=filepath)
                self.db.add_slide(slide, after=after_index)
                count += 1
        return count

    def on_crop_image_slide_button_click(self):
        if not self.active_slide or self.active_slide.allow_cropping:
            return
        if not self.crop_rect or self.crop_rect.get_width()<10:
            return
        rect = self.slide_image.canvas2image(self.crop_rect)
        new_image_slide = self.active_slide.crop(rect)
        self.db.add_slide(new_image_slide, after=self.active_slide_index)
        self.show_slide(1)

    def on_add_image_slide_button_click(self):
        image_files = self.get_image_files_from_user()
        if not image_files or \
           self.add_image_files(image_files, self.active_slide_index) == 0:
            messagebox.showerror(
                "Error", "No proper image file is available to import")
        else:
            self.show_slide(1)

    def on_add_text_slide_button_click(self):
        text=simpledialog.askstring("Text Slide", "Enter text to display")
        if text:
            text = text.strip()
        if text:
            text_slide = TextSlide(text=text)
            self.db.add_slide(text_slide, before=self.active_slide_index)
            self.show_slide(0)
        else:
            messagebox.showerror(
                "Error", "You need to provide some text to create a text slide.")

    def on_delete_slide_button_click(self):
        if self.db.slide_count == 1:
            messagebox.showerror(
                "Low slide count", "You need to keep at least one slide in the project.")
            return
        if messagebox.askyesno("Delete Slide", "Do you really want to delete this slide?"):
            self.db.remove_slide(self.active_slide_index)
            self.active_slide_index = min(self.active_slide_index, self.db.slide_count-1)
            self.show_slide(0)

    def on_create_project_button_click(self):
        project_filename= self.open_or_create_file(open=False)
        if not project_filename:
            return
        self.db = None
        for i in range(2):
            image_files = self.get_image_files_from_user()
            if not image_files:
                messagebox.showerror("Error",
                                     "You need to select at least one image to create the project.")
                continue
            self.db = ProjectDb()
            self.db.set_filepath(project_filename)
            self.add_image_files(image_files)
            self.db.save()
            break

        if self.db and self.db.slide_count:
            self.destroy_project_widgets()
            self.create_editing_widgets()
            self.show_slide()
        else:
            messagebox.showerror("Error", "Unable to create new project!")

    def on_open_project_button_click(self):
        project_filename= self.open_or_create_file(open=True)
        if not project_filename:
            return
        self.db = ProjectDb(project_filename)

        self.destroy_project_widgets()
        self.create_editing_widgets()
        self.show_slide(0)

    def on_quit_project_button_click(self):
        self.on_window_close()

    def on_preview_button_click(self):
        if self.preview_player:
            return
        self.video_frame_maker = VideoFrameMaker(self.db.slides, self.app_config)
        self.preview_player = PreviewPlayer(
            self, self.video_frame_maker, self.app_config, self.on_preview_window_close)
        show_tk_widget_at_center(self.preview_player.top, use_req=True)
        self.preview_player.top.bind("WM_DELETE_WINDOW", self.on_preview_window_close)
        self.wait_window(self.preview_player.top)

    def on_close_editing_button_click(self):
        if self.preview_player:
            self.preview_player.close()
            self.preview_player = None

        self.destroy_editing_widgets()
        self.create_project_widgets()

    def on_text_alignment_select(self, event):
        sel = self.text_alignlist.curselection()
        if sel and sel[0]<len(self.text_align_options):
            align = self.text_align_options[sel[0]]
            self.active_slide.set_caption_alignment(align)
            if self.active_slide.TypeName == ImageSlide.TypeName:
                self.update_image_slide_on_canvas()

    def on_key_in_caption_text(self, event):
        if not self.active_slide:
            return
        text = self.caption_text.get(1.0, tk.END)
        if self.active_slide.TypeName == ImageSlide.TypeName:
            self.active_slide.set_caption(text)
            self.update_image_slide_on_canvas()
        elif self.active_slide.TypeName == TextSlide.TypeName:
            self.active_slide.set_text(text)
            self.update_text_slide_on_canvas()


    def on_filter_check_button_change(self):
        filters = []
        for filter_check_button in self.filter_check_buttons.values():
            if filter_check_button.filter_var.get() == 1:
                filters.append(filter_check_button.filter_code)
        self.active_slide.set_filters(filters)
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
        elif self.movable_rect:
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

        video_wh = self.app_config.video_resolution
        self.canvas.scale = min(canvas_width/video_wh.x, canvas_height/video_wh.y)

        self.canvas_active_area.set_cxy_wh(
            cx = canvas_width*0.5, cy=canvas_height*0.5,
            w=video_wh.x*self.canvas.scale, h=video_wh.y*self.canvas.scale)

        self.canvas.coords(self.canvas_background,
                           self.canvas_active_area.x1, self.canvas_active_area.y1,
                           self.canvas_active_area.x2, self.canvas_active_area.y2)
        self.show_slide(0)

    def on_preview_window_close(self):
        self.preview_player = None

    def on_window_close(self):
        if self.preview_player:
            self.preview_player.close()
            self.preview_player = None

        if self.frame_mode == self.FRAME_MODE_EDITING:
            self.destroy_editing_widgets()
            self.create_project_widgets()
            return
        self.master.destroy()

    def update_canvas_rects(self):
        if self.crop_rect:
            self.crop_rect.adjust_to_aspect_ratio(self.app_config.aspect_ratio)
            self.set_canvas_rect(self.canvas.crop_rect, self.crop_rect)
        if self.corner_rect:
            self.corner_rect.set_cxy_wh(cx=self.crop_rect.x2,
                                    cy=self.crop_rect.y2, w=5, h=5)
            self.set_canvas_rect(self.canvas.corner_rect, self.corner_rect)

    def set_canvas_rect(self, canvas_rect, rect):
        self.canvas.coords(canvas_rect, rect.x1, rect.y1, rect.x2, rect.y2)

class Root(tk.Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Img2Vid")

    def show_at_center(self):
        show_tk_widget_at_center(self)

    def resize(self, width, height):
        self.geometry('{}x{}'.format(width, height))

def is_magick_found():
    try:
        import wand.api
    except ImportError as e:
        return False
    return True

import traceback
def get_magick_error():
    try:
        import wand.api
    except ImportError as e:
        return str(traceback.format_exc())
    return ""

while not is_magick_found():
    from commons import EnvironConfig
    environ_config = EnvironConfig(os.path.join(THIS_DIR, "environ.ini"))
    if environ_config.get_magick_home():
        os.environ["MAGICK_HOME"] = environ_config.get_magick_home()
    if not is_magick_found():
        from magick_home_loader import MagickHomeLoader
        tk_root = Root()
        app = MagickHomeLoader(master=tk_root,
                               config=environ_config,
                               error_msg = get_magick_error())
        tk_root.show_at_center()
        app.mainloop()
        if app.closing:
            break

if is_magick_found():
    from commons import Point, Rectangle, AppConfig
    import commons.image_utils as image_utils
    from project_db import ProjectDb
    from ui_tk import CanvasImage, PreviewPlayer
    from slides import TextSlide, ImageSlide, VideoFrameMaker, Slide

    tk_root = Root()
    app = Application(master=tk_root)
    tk_root.show_at_center()
    app.mainloop()
