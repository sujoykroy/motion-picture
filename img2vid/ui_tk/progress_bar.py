import tkinter as tk

class ProgressBar(tk.Canvas):
    def __init__(self, master, fill, **kwargs):
        super(ProgressBar, self).__init__(master=master, **kwargs)
        self.progress = 0
        self.rect = self.create_rectangle(0, 0, 0, 0, fill=fill)
        self.bind("<Configure>", self.on_canvas_resize)

    def on_canvas_resize(self, event):
        self.redraw()

    def set_progress(self, value):
        self.progress = value
        self.redraw()

    def redraw(self):
        self.coords(
            self.rect, 0, 0,
            self.winfo_width()*self.progress,
            self.winfo_height())
