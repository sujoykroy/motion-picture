import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as tkscrolledtext

from ..analysers import TextAnalyser
from .frame import Frame

class TextPropEditor(Frame):
    def __init__(self, master, app_config):
        super().__init__(
            master=master,
            app_config=app_config,
            event_names=["caption_updated"]
        )
        self._caption = None

        self.widgets.text_label = self._create_label("Caption")
        self.widgets.text = tkscrolledtext.ScrolledText(
            self.base, height="5", width="40")
        self.widgets.text.pack()
        self.widgets.text.bind("<KeyRelease>", self._text_changed)

        self.widgets.font_family_label = self._create_label("Font Familiy")
        self.widgets.font_family_combo = ttk.Combobox(
            self.base, values=TextAnalyser.get_font_families())
        self.widgets.font_family_combo.bind(
            "<<ComboboxSelected>>", self._set_font_family)
        self.widgets.font_family_combo.pack()

        self.widgets.font_style_label = self._create_label("Font Style")
        self.widgets.font_style_combo = ttk.Combobox(
            self.base, values=TextAnalyser.get_font_styles())
        self.widgets.font_style_combo.bind(
            "<<ComboboxSelected>>", self._set_font_style)
        self.widgets.font_style_combo.pack()

        self.widgets.font_size_label = self._create_label("Font Size", 5)
        self.widgets.font_size_scale = tk.Scale(
            self.base, from_=1, to=50, resolution=1,
            orient=tk.HORIZONTAL, command=self._set_font_size)
        self.widgets.font_size_scale.pack(expand=1, fill=tk.X)

        self.widgets.apply_button = self._create_button(
            "Apply", self._apply_slide_change, None)

    def set_caption(self, caption, text_config):
        self.widgets.text.delete("1.0", tk.END)
        self._caption = caption
        if not self._caption:
            return
        self.widgets.text.insert(tk.END, self._caption.text)
        self.widgets.font_family_combo.set(self._caption.font_family)
        self.widgets.font_style_combo.set(self._caption.font_style)

        font_size = self._caption.font_size
        if not font_size:
            font_size = text_config.font_size
        self.widgets.font_size_scale.set(font_size)

    def _text_changed(self, _event):
        if not self._caption:
            return
        text = self.widgets.text.get(1.0, tk.END)
        self._caption.text = text
        self.events.caption_updated.fire()

    def _apply_slide_change(self):
        self.events.caption_updated.fire()

    def _set_font_family(self, _):
        self._caption.font_family = self.widgets.font_family_combo.get()
        self.events.caption_updated.fire()

    def _set_font_style(self, _):
        self._caption.font_style = self.widgets.font_style_combo.get()
        self.events.caption_updated.fire()

    def _set_font_size(self, _):
        self._caption.font_size = self.widgets.font_size_scale.get()
        self.events.caption_updated.fire()

    def _create_label(self, text, pady=0):
        label = tk.Label(self.base, text=text)
        label.pack(pady=pady)
        return label

    def _create_button(self, text, command, side):
        button = tk.Button(self.base, text=text, command=command)
        button.pack(side=side)
        return button
