import tkinter as tk
from tkinter import filedialog
import tkinter.scrolledtext as tkscrolledtext

from ..configs import EnvironConfig
from .base_app import BaseApp

class MagickHomeLoader(BaseApp):
    def __init__(self):
        super().__init__(
            title="Magick Home Loader", width=400, height=200)

        self.config = EnvironConfig()
        self.protocol("WM_DELETE_WINDOW", self._close_window)

        self.frame = tk.Frame(self)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=2)

        self.frame.label = tk.Label(
            self.frame,
            text="ImageMagick library could not be found.\n" +
            "Select/Type the folder where it is stored.")
        self.frame.label.grid(row=0, column=0, columnspan=2)

        self.error_text = tkscrolledtext.ScrolledText(self.frame, height="5", width="40")
        self.error_text.grid(row=1, column=0, columnspan=2, sticky=tk.E+tk.W+tk.N+tk.S)
        self.error_text["state"] = tk.DISABLED

        self.folder_var = tk.StringVar()
        self.folder_var.set(
            self.config.get_variable(self.config.MAGICK_HOME))
        self.frame.entry = tk.Entry(self.frame, textvariable=self.folder_var)
        self.frame.entry.grid(row=2, column=0, sticky=tk.E+tk.W)

        self.frame.folder_button = tk.Button(
            self.frame, text="Select Folder",
            command=self.select_folder)
        self.frame.folder_button.grid(row=2, column=1)

        self.frame.proceed_button = tk.Button(
            self.frame, text="Proceed", command=self.proceed)
        self.frame.proceed_button.grid(row=3, column=0, sticky=tk.W)

        self.frame.close_button = tk.Button(
            self.frame, text="Close", command=self._close_window)
        self.frame.close_button.grid(row=3, column=1, sticky=tk.E)

        self._show_error()

    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def proceed(self):
        self.config.set_variable(
            self.config.MAGICK_HOME, self.folder_var.get())
        self.config.load_variable(self.config.MAGICK_HOME)
        self.config.save()
        if self.config.is_magick_found():
            self._close_window()
        else:
            self._show_error()

    def _show_error(self):
        msg = "Unable to load ImageMagick library.\n"
        msg += "Please make sure it is avaialble at specified path.\n"
        msg += self.config.get_magick_names()
        msg += "\nDebug:\n" +  self.config.get_magick_error()

        self.error_text["state"] = tk.NORMAL
        self.error_text.delete(1.0, tk.END)
        self.error_text.insert(tk.END, msg)
        #self.error_text["state"] = tk.DISABLED

    def _close_window(self):
        self.destroy()
