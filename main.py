import os
import configparser
import json
from collections import OrderedDict

import tkinter as tk
from tkinter import filedialog

from project_db import ProjectDb, TextSlide, ImageSlide

THIS_DIR = os.path.abspath(__file__)

class Application(tk.Frame):
    def __init__(self, master=None, config_filename="app.ini"):
        super(Application, self).__init__(master=master)

        #load configuration
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(THIS_DIR, config_filename))

        #prompt for project filename
        project_filename = ""
        """
        project_filename= filedialog.asksaveasfilename(
                                    filetypes=[("JSON", "*.json")])
        """
        self.db = ProjectDb(project_filename)

        #image_dir = filedialog.askdirectory()
        image_dir = "/home/sujoy/Pictures/temp3"
        self.load_files_from_dir(image_dir)

    def load_files_from_dir(self, dir):
        for filename in os.listdir(dir):
            print("filename", filename)
            root, ext = os.path.splitext(filename)
            if ext in (".jpg", ".png"):
                filepath = os.path.join(dir, filename)
                slide = ImageSlide(filepath=filepath)
                self.db.add_slide(slide)


tk_root = tk.Tk()
tk_root.title("Img2Vid")

app = Application(master=tk_root)
app.mainloop()
