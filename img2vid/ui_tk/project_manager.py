"""This module holds basic project management class"""
import tkinter as tk

from .frame import Frame
from .dialog import Dialog

PADDING = 5

class ProjectManager(Frame):
    """
    Basic interface to allow use to create/open project
    """
    def __init__(self, master):
        super().__init__(
            master=master,
            event_names=["open_project", "create_project", "quit"])

        self.buttons = []
        self._create_button("Create New Project", self._on_create)
        self._create_button("Open Existing Project", self._on_open)
        self._create_button("Quit", self._on_quit)

    def _create_button(self, text, command):
        button = tk.Button(self.base, text=text, command=command)
        button.pack(padx=PADDING, pady=PADDING, fill=tk.BOTH, expand=1)
        self.buttons.append(button)

    def _on_create(self):
        """Called after clicking 'Create Project' button."""
        filepath = Dialog.ask_for_project_file(create_new=True)
        if filepath:
            self.events.create_project.fire(filepath=filepath, create_new=True)

    def _on_open(self):
        """Called after clicking 'Open Project' button."""
        filepath = Dialog.ask_for_project_file(create_new=False)
        if filepath:
            self.events.open_project.fire(filepath=filepath, create_new=False)

    def _on_quit(self):
        """Called after clicking 'Quit' button."""
        self.events.quit.fire()
