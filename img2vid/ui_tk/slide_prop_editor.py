import tkinter as tk
import tkinter.ttk as ttk

from .frame import Frame
from .dialog import Dialog
from .text_prop_editor import TextPropEditor

from ..slides import ImageSlide, TextSlide

class TextTab:
    def __init__(self, frame_base, app_config):
        self.editor = TextPropEditor(frame_base, app_config)
        self.tab_id = None
        self.notebook = None

    def attach(self, tab_text, notebook):
        self.notebook = notebook
        self.notebook.add(self.editor.base, text=tab_text)
        self.tab_id = notebook.tabs()[-1]

    def show(self):
        self.notebook.add(self.editor.base)
        self.notebook.select(self.editor.base)

    def hide(self):
        self.notebook.hide(self.editor.base)

class SlidePropEditor(Frame):
    def __init__(self, master, app_config):
        super().__init__(
            master=master,
            app_config=app_config,
            event_names=["slide_updated", "crop_slide", "delete_slide"]
        )
        self._slide = None

        self.widgets.notebook = ttk.Notebook(self.base)
        self.widgets.notebook.pack()

        self.text_tabs = {}
        for name in ImageSlide.CAP_ALIGNMENTS + ['text']:
            tab = TextTab(self.base, app_config)
            self.text_tabs[name] = tab
            tab.attach(name, self.widgets.notebook)
            tab.editor.events.caption_updated.bind(self._caption_updated)

        self.widgets.effects_label = self._create_label("Effects", pady=5)

        self.widgets.effects_frame = tk.Frame(self.base)
        self.widgets.effects_frame.pack()

        self.widgets.effect_checks = dict()
        for effect_name in sorted(app_config.effects.keys()):
            effect_config = app_config.effects[effect_name]

            effect_var = tk.IntVar()
            check_button = tk.Checkbutton(
                self.widgets.effects_frame, text=effect_name,
                variable=effect_var, command=self._effect_check_changed)
            check_button.pack(anchor=tk.W)

            check_button.effect_var = effect_var
            check_button.effect_name = effect_name
            check_button.effect_config = effect_config
            self.widgets.effect_checks[effect_name] = check_button

        self.widgets.crop_button = self._create_button(
            "Crop", self._crop, tk.BOTTOM)
        self.widgets.delete_slide_button = self._create_button(
            "Delete Slide", self._delete_slide, tk.BOTTOM)

    def set_slide(self, slide):
        for check_button in self.widgets.effect_checks.values():
            check_button.effect_var.set(0)

        #Hide all tabs
        for tab_name in self.text_tabs:
            self.text_tabs[tab_name].hide()

        self._slide = slide
        if not self._slide:
            return

        if isinstance(self._slide, TextSlide):
            align_state = tk.DISABLED
            tab = self.text_tabs['text']
            tab.editor.set_caption(
                self._slide.caption, self.app_config.text)
            tab.show()
        else:
            align_state = tk.NORMAL
            for cap_name in ImageSlide.CAP_ALIGNMENTS:
                tab = self.text_tabs[cap_name]
                tab.editor.set_caption(
                    self._slide.get_caption(cap_name), self.app_config.image)
                tab.show()

        self.widgets.crop_button["state"] = align_state

        for effect_name in self._slide.effects:
            check_button = self.widgets.effect_checks.get(effect_name)
            if check_button:
                check_button.effect_var.set(1)

    def _effect_check_changed(self):
        if not self._slide:
            return
        for check_button in self.widgets.effect_checks.values():
            effect_config = check_button.effect_config
            checked = check_button.effect_var.get()
            if checked:
                self._slide.add_effect(
                    effect_config.effect_class, effect_config.defaults)
            else:
                self._slide.remove_effect(check_button.effect_name)

    def _crop(self):
        if not self._slide:
            return
        self.events.crop_slide.fire()

    def _delete_slide(self):
        if not self._slide:
            return
        yes = Dialog.ask_yes_or_no(
            "Delete Slide",
            "Do you really want to delete this slide?")
        if yes:
            self.events.delete_slide.fire()

    def _caption_updated(self):
        self.events.slide_updated.fire()

    def _create_label(self, text, pady=0):
        label = tk.Label(self.base, text=text)
        label.pack(pady=pady)
        return label

    def _create_button(self, text, command, side):
        button = tk.Button(self.base, text=text, command=command)
        button.pack(side=side)
        return button
