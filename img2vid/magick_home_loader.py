import tkinter as tk
import os
from tkinter import filedialog

class MagickHomeLoader(tk.Frame):
    def __init__(self, master, config):
        super(MagickHomeLoader, self).__init__(master=master)
        self.closing = False
        self.config = config
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.pack(expand=True, fill=tk.BOTH)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.label = tk.Label(
                    self,
                    text="ImageMagick library could not be found.\n" +
                         "Select/Type the folder where it is stored.")
        self.label.grid(row=0, column=0, columnspan=2, sticky=tk.E+tk.W+tk.N+tk.S)

        self.folder_var = tk.StringVar()
        self.folder_var.set(self.config.get_magick_home())
        self.entry = tk.Entry(self, textvariable=self.folder_var)
        self.entry.grid(row=1, column=0, sticky=tk.E+tk.W)
        self.folder_button = tk.Button(self, text="Select Folder",
                                       command=self.select_folder)
        self.folder_button.grid(row=1, column=1)
        self.proceed_button = tk.Button(self, text="Proceed", command=self.proceed)
        self.proceed_button.grid(row=2, column=0, columnspan=2)

    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def proceed(self):
        self.config.set_magick_home(self.folder_var.get())
        self.master.destroy()

    def on_window_close(self):
        self.closing = True
        self.master.destroy()