"""This module holds the main GUI class to start tk-based img2vid application"""
import tkinter as tk

class MainApp(tk.Tk):
    """Main GUI Application Class.

    Only one instance of this class is supposed to be created.

    Parameters
    ----------
    title : str
    width : :obj:`int`
    height : :obj:`int`
    """
    def __init__(self, title, width, height):
        super(MainApp, self).__init__()
        self.title(title)
        self._resize(width, height)
        self._show_at_center()

    def _show_at_center(self):
        """Shows the widget at the center of the screen."""
        for _ in range(2):
            self.withdraw()
            self.update_idletasks()
            left = (self.winfo_screenwidth() - self.winfo_width()) / 2
            top = (self.winfo_screenheight() - self.winfo_height()) / 2
            self.geometry("+%d+%d" % (left, top))
            self.deiconify()
            self.update_idletasks()

    def _resize(self, width, height):
        """Fit the widget inside the box of given width and height."""
        self.geometry('{}x{}'.format(width, height))
