import tkinter as tk
from .utils import UtilsTk

class BaseApp(tk.Tk):
    def __init__(self, title, width, height):
        super().__init__()
        self.title(title)
        self.resize(width, height)
        self.show_at_center()

    def show_at_center(self):
        UtilsTk.show_widget_at_center(self)

    def resize(self, width, height):
        """Fit the widget inside the box of given width and height."""
        self.geometry('{}x{}'.format(width, height))
