import tkinter as tk

class ProgressBar(tk.Canvas):
    def __init__(self, master, fill, **kwargs):
        super(ProgressBar, self).__init__(master=master, **kwargs)
        self.progress = 0
        self.rect = self.create_rectangle(0, 0, 0, 0, fill=fill)
        self.text_ob = self.create_text(0, 0, justify="center", anchor=tk.CENTER)
        self.bind("<Configure>", self.on_canvas_resize)

    def on_canvas_resize(self, event):
        self.redraw()

    def set_progress(self, value):
        self.progress = value
        self.redraw()

    def set_text(self, text):
        self.itemconfig(self.text_ob, text=text)

    def redraw(self):
        self.itemconfig(self.rect, state=(tk.HIDDEN if self.progress==0 else tk.NORMAL))
        self.coords(
            self.rect, 0, 0,
            self.winfo_width()*self.progress,
            self.winfo_height())
        self.coords(self.text_ob, self.winfo_width()*0.5, self.winfo_height()*0.5)