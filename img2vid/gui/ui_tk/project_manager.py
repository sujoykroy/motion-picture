import os
import tkinter as tk

from .dialog import Dialog

PADDING = 5

class ProjectManager(tk.Frame):
    def __init__(self, master,
                 create_callback, open_callback, quit_callback):
        super(ProjectManager, self).__init__(master=master)

        self._create_button = tk.Button(
            self,text="Create New Project", command=self.on_create)
        self._create_button.pack(
            padx=PADDING, pady=PADDING, fill=tk.BOTH, expand=1)
        self._create_button.callback = create_callback

        self._open_button = tk.Button(
            self, text="Open Existing Project",
            command=self.on_open)
        self._open_button.pack(
            padx=PADDING, pady=PADDING, fill=tk.BOTH, expand=1)
        self._open_button.callback = open_callback

        self._quit_button = tk.Button(
            self, text="Quit", command=self.on_quit)
        self._quit_button.pack(
            padx=PADDING, pady=PADDING, fill=tk.BOTH, expand=1)
        self._quit_button.callback = quit_callback

    def on_create(self):
        filepath = Dialog.ask_for_project_file()
        if filepath and self._create_button.callback:
            self._create_button.callback(filepath)

    def on_open(self):
        filepath = Dialog.ask_for_project_file(open=True)
        if filepath and self._open_button.callback:
            self._open_button.callback(filepath)

    def on_quit(self):
        if self._quit_button.callback:
            self._quit_button.callback()
