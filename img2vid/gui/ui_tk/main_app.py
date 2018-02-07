"""This module holds the main GUI class to start tk-based img2vid application"""
import sys
import tkinter as tk

from .project_manager import ProjectManager

MODE_PROJECT_MANAGE = 0

class MainApp(tk.Tk):
    """Main GUI Application Class.

    Only one instance of this class is supposed to be created.

    :param title:
    :param width:
    :param height:
    """
    def __init__(self, title, width, height):
        super(MainApp, self).__init__()
        self.protocol("WM_DELETE_WINDOW", self._close_window)

        self.title(title)
        self._resize(width, height)
        self._show_at_center()

        self.active_frame = None
        self._set_frame_mode(MODE_PROJECT_MANAGE)

    def _set_frame_mode(self, mode):
        """This method will show correct frame based on mode.

        For example, it may show screen to manager project,
        or it may show screen to change slides.
        """
        new_frame = None
        if mode == MODE_PROJECT_MANAGE:
            new_frame = ProjectManager(
                self,
                open_callback = self.load_project,
                create_callback = self.load_project,
                quit_callback=self._close_window)

        new_frame.pack(fill=tk.BOTH, expand=1)
        self.active_frame = new_frame

    def start(self):
        """Start the main eventloop of Tk Application."""
        self.mainloop()
        try:
            sys.exit()
        except SystemExit:
            pass

    def load_project(self, filepath):
        pass

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

    def _close_window(self):
        """This will close MainApp."""
        self.destroy()
