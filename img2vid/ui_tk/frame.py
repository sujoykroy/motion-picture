import tkinter as tk
from types import SimpleNamespace

class EventHandler:
    def __init__(self):
        self.callbacks = []

    def bind(self, callback):
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def fire(self, **kwargs):
        for callback in self.callbacks:
            callback(**kwargs)

class Frame:
    def __init__(self, master, app_config=None, event_names=None):
        self.base = tk.Frame(master=master)
        self.app_config = app_config
        self.widgets = SimpleNamespace()

        event_handlers = {}
        if event_names:
            for event_name in event_names:
                event_handlers[event_name] = EventHandler()
        self.events = SimpleNamespace(**event_handlers)

    def pack(self, **kwargs):
        self.base.pack(**kwargs)

    def grid(self, **kwargs):
        self.base.grid(kwargs)

    def destroy(self):
        self.base.destroy()
