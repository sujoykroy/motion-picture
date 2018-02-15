"""This module holds the main GUI class to start img2vid application"""
import sys
import os
from enum import Enum
import tkinter as tk

from ..slides import Project
from ..configs import AppConfig

from .dialog import Dialog
from .project_manager import ProjectManager
from .slide_editor import SlideEditor
from .base_app import BaseApp

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

class FlowMode(Enum):
    NONE = 0
    PROJECT_MANAGE = 1
    PROJECT_SHOW = 2

class MainApp(BaseApp):
    """Main GUI Application Class.

    Only one instance of this class is supposed to be created.

    :param title:
    :param width:
    :param height:
    """
    def __init__(self, title, width, height):
        super().__init__(title, width, height)
        self.protocol("WM_DELETE_WINDOW", self._close_window)

        self._flow_mode = FlowMode.NONE
        self._active_frame = None
        self._project = None
        self._config = AppConfig()
        self._set_frame_mode(FlowMode.PROJECT_MANAGE)

    def start(self):
        """Start the main eventloop of Tk Application."""
        self.mainloop()
        try:
            sys.exit()
        except SystemExit:
            pass

    def load_project(self, filepath, create_new):
        """Loads a project from given filepath.
        If given project does not exit, user will be asked to
        import images and new project will be created."""
        if create_new:
            for _ in range(2):
                image_files = Dialog.ask_for_image_files(self._config.image_types)
                if not image_files:
                    error_msg = "You need to select at least one image " +\
                                "to create the project."
                    Dialog.show_error("Error", error_msg)
                else:
                    break
            if not image_files:
                error_msg = "No project has been created."
                Dialog.show_error("Error", error_msg)
                return
            self._project = Project()
            self._project.add_image_files(image_files)
            self._project.save(filepath)
        else:
            self._project = Project()
            self._project.load_from(filepath)
        self._set_frame_mode(FlowMode.PROJECT_SHOW)

    def _set_frame_mode(self, mode):
        """This method will show correct frame based on mode.

        For example, it may show screen to manager project,
        or it may show screen to change slides.
        """
        if self._flow_mode == mode:
            return
        new_frame = None
        if mode == FlowMode.PROJECT_MANAGE:
            new_frame = ProjectManager(self)
            new_frame.events.open_project.bind(self.load_project)
            new_frame.events.create_project.bind(self.load_project)
            new_frame.events.quit.bind(self._close_window)
        elif mode == FlowMode.PROJECT_SHOW:
            new_frame = SlideEditor(self, self._config, self._project)
            new_frame.events.close.bind(self._show_project_manager)
        if new_frame:
            if self._active_frame:
                self._active_frame.destroy()
            new_frame.pack(fill=tk.BOTH, expand=1)
        self._active_frame = new_frame

    def _show_project_manager(self):
        self._set_frame_mode(FlowMode.PROJECT_MANAGE)

    def _close_window(self):
        """This will close MainApp."""
        if self._project:
            self._project.save()
        self.destroy()
