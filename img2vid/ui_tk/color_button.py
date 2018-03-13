import tkinter as tk

import PIL.ImageTk
import tkcolorpicker

from ..renderer import ImageRenderer

class ColorButton:
    def __init__(self, parent, title, width, height, command):
        self._width = width
        self._height = height
        self._title = title
        self.base = tk.Button(parent, command=self._pick_color)
        self._command = command
        self._image = None
        self._image_tk = None
        self._color = None
        self.color = "#FFFFFF00"

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._image = ImageRenderer.create_blank(self._width, self._height, color)
        self._image_tk = PIL.ImageTk.PhotoImage(image=self._image)
        self.base["image"] = self._image_tk
        self._color = color

    def _pick_color(self):
        _, new_color = tkcolorpicker.askcolor(
            color=self._color, parent=self.base,
            title=("Choose {}".format(self._title)), alpha=True)
        if new_color is None:
            return
        self.color = new_color
        if self._command:
            self._command()
