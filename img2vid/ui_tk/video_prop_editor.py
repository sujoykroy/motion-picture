import tkinter as tk

from .frame import Frame

class VideoPropEditor(Frame):
    def __init__(self, master, app_config):
        super().__init__(
            master=master,
            app_config=app_config,
            event_names=["video_updated"]
        )
        self._slide = None
        self.widgets.start_at_label = self._create_label("Start At", 5)
        self.widgets.start_at_scale = tk.Scale(
            self.base, from_=0, to=100, resolution=1,
            orient=tk.HORIZONTAL, command=self._set_start_at)
        self.widgets.start_at_scale.pack(fill=tk.X)

        self.widgets.end_at_label = self._create_label("End At", 5)
        self.widgets.end_at_scale = tk.Scale(
            self.base, from_=0, to=100, resolution=1,
            orient=tk.HORIZONTAL, command=self._set_end_at)
        self.widgets.end_at_scale.pack(fill=tk.X)

    def set_slide(self, slide):
        self._slide = slide
        self.widgets.start_at_scale["to"] = slide.full_duration
        self.widgets.end_at_scale["to"] = slide.full_duration

        self.widgets.start_at_scale.set(slide.start_at)
        self.widgets.end_at_scale.set(slide.end_at)

    def _set_start_at(self, _):
        self._slide.start_at = self.widgets.start_at_scale.get()
        self._slide.abs_current_pos = self.widgets.start_at_scale.get()
        self.events.video_updated.fire()

    def _set_end_at(self, _):
        self._slide.end_at = self.widgets.end_at_scale.get()
        self._slide.abs_current_pos = self.widgets.end_at_scale.get()
        self.events.video_updated.fire()

    def _create_label(self, text, pady=0, parent=None):
        if parent is None:
            parent = self.base
        label = tk.Label(parent, text=text)
        label.pack(pady=pady)
        return label
