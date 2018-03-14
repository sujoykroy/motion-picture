"""This module provides basic dialogs"""
import os
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

class Dialog:
    """Provider of basic dialogs, mostly called as staticmethods"""

    @staticmethod
    def ask_for_project_file(create_new=False):
        """Open project file selection to open/create a project

        :param create_new: Where to open existing file or to create new one
        :type create_new: :class:`bool`
        :returns: Selected/Typed filepath
        :rtype: :class:`str`

        """
        filetypes = [("JSON", "*.json")]
        start_dir = os.path.expanduser("~")
        if not create_new:
            project_filename = filedialog.askopenfilename(
                filetypes=filetypes,
                initialdir=start_dir,
                title="Select a project file to open")
        else:
            project_filename = filedialog.asksaveasfilename(
                filetypes=filetypes,
                initialdir=start_dir,
                title="Choose folder and write filename to save new project")
        if project_filename:
            _, ext = os.path.splitext(project_filename)
            if ext != ".json":
                project_filename += ".json"
        return project_filename

    @staticmethod
    def ask_for_image_files(file_types, start_dir=None):
        """Open filedialog to select multiple image files

        :param file_types: list of allowed file types
        :type file_types: :class:`List[Tuple[str, str]]`
        :returns: Selected filepaths
        :rtype: :class:`List[str]`

        """
        image_files = filedialog.askopenfilenames(
            title="Select images to import", filetypes=file_types,
            initialdir=start_dir)
        return image_files

    @staticmethod
    def ask_for_video_files(file_types, start_dir=None):
        """Open filedialog to select multiple video files

        :param file_types: list of allowed file types
        :type file_types: :class:`List[Tuple[str, str]]`
        :returns: Selected filepaths
        :rtype: :class:`List[str]`

        """
        video_files = filedialog.askopenfilenames(
            title="Select videos to import", filetypes=file_types,
            initialdir=start_dir)
        return video_files

    @staticmethod
    def ask_for_new_video_file(file_types, default_ext):
        """Open filedialog to select video file"""
        start_dir = os.path.expanduser("~")
        video_file = filedialog.asksaveasfilename(
            initialdir=start_dir,
            title="Save video as", filetypes=file_types)
        if video_file:
            _, ext = os.path.splitext(video_file)
            if not ext:
                video_file += default_ext
        return video_file

    @staticmethod
    def ask_for_text(title, desc):
        result = simpledialog.askstring(title, desc)
        if result:
            result = result.strip()
        return result

    @staticmethod
    def ask_yes_or_no(title, question):
        return messagebox.askyesno(title, question)

    @staticmethod
    def show_error(title, msg):
        """Shows error message."""
        messagebox.showerror(title, msg)

    @staticmethod
    def show_info(title, msg):
        """Shows Info message."""
        messagebox.showinfo(title, msg)
