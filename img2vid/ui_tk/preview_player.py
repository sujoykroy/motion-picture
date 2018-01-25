import tkinter as tk

from commons import Rectangle
from .canvas_image import CanvasImage

class PreviewPlayer:
    def __init__(self, parent, video_frame_maker):
        self.fps = 10
        self.millisecond_per_frame = 1/self.fps
        self.video_frame_maker = video_frame_maker
        top = self.top = tk.Toplevel(parent)

        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(top, highlightbackground="black")
        self.canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)

        self.slider = tk.Scale(top, from_=0, to=self.video_frame_maker.duration,
                               orient=tk.HORIZONTAL, resolution=1/(self.video_frame_maker.duration*self.fps),
                               command=self.on_slider_change)
        self.slider.grid(row=1, column=0, sticky=tk.S+tk.W+tk.E)

        self.canvas_area = Rectangle()
        self.canvas.image = None

        self.slider_alaram_period = int(1000/self.fps)
        self.frame_alaram_period = self.slider_alaram_period*5
        self.slider_alarm = self.top.after(self.slider_alaram_period, self.move_forward)
        self.frame_alarm = self.top.after(self.frame_alaram_period, self.show_frame)

    def move_forward(self):
        self.slider.set(self.slider.get()+1/self.fps)
        self.slider_alarm = self.top.after(int(1000/self.fps), self.move_forward)

    def show_frame(self):
        t = self.slider.get()
        self.canvas_area.set_values(
            x2=self.canvas.winfo_width(), y2=self.canvas.winfo_height())
        image = self.video_frame_maker.get_image_at(t)
        self.canvas_image = CanvasImage(image, self.canvas_area)
        if self.canvas.image:
            self.canvas.delete(self.canvas.image)

        self.canvas.image = self.canvas.create_image(
                self.canvas_image.offset.x, self.canvas_image.offset.y,
                image=self.canvas_image.tk_image, anchor="nw")
        self.frame_alarm = self.top.after(self.frame_alaram_period, self.show_frame)

    def on_slider_change(self, event):
        pass