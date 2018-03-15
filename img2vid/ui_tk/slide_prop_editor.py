import tkinter as tk
import tkinter.ttk as ttk

from .frame import Frame
from .dialog import Dialog
from .text_prop_editor import TextPropEditor
from .video_prop_editor import VideoPropEditor
from .effects_prop_editor import EffectsPropEditor

from ..slides import ImageSlide, TextSlide, VideoSlide

class EditorTab:
    def __init__(self, editor):
        self.editor = editor
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

        self.editor_tabs = {}
        for name in ImageSlide.CAP_ALIGNMENTS + ['text']:
            tab = self._add_editor_tab(name, TextPropEditor(self.base, app_config))
            tab.editor.events.caption_updated.bind(self._slide_updated)

        tab = self._add_editor_tab('video', VideoPropEditor(self.base, app_config))
        tab.editor.events.video_updated.bind(self._slide_updated)

        tab = self._add_editor_tab('effects', EffectsPropEditor(self.base, app_config))
        tab.editor.events.effects_updated.bind(self._slide_updated)

        self.widgets.crop_button = self._create_button(
            "Crop", self._crop, tk.BOTTOM)
        self.widgets.delete_slide_button = self._create_button(
            "Delete Slide", self._delete_slide, tk.BOTTOM)

    def set_slide(self, slide):
        #Hide all tabs
        for tab_name in self.editor_tabs:
            self.editor_tabs[tab_name].hide()

        self._slide = slide
        if not self._slide:
            return

        if isinstance(self._slide, TextSlide):
            align_state = tk.DISABLED
            tab = self.editor_tabs['text']
            tab.editor.set_caption(
                self._slide.caption, self.app_config.text)
            tab.show()
        else:
            align_state = tk.NORMAL
            for cap_name in ImageSlide.CAP_ALIGNMENTS:
                tab = self.editor_tabs[cap_name]
                tab.editor.set_caption(
                    self._slide.get_caption(cap_name), self.app_config.image)
                tab.show()
            if slide.TYPE_NAME == VideoSlide.TYPE_NAME:
                tab = self.editor_tabs['video']
                tab.editor.set_slide(self._slide)
                tab.show()

        tab = self.editor_tabs['effects']
        tab.editor.set_slide(slide)
        tab.show()

        self.widgets.crop_button["state"] = align_state

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

    def _slide_updated(self):
        self.events.slide_updated.fire()

    def _add_editor_tab(self, name, editor):
        tab = EditorTab(editor)
        self.editor_tabs[name] = tab
        tab.attach(name, self.widgets.notebook)
        return tab

    def _create_label(self, text, pady=0):
        label = tk.Label(self.base, text=text)
        label.pack(pady=pady)
        return label

    def _create_button(self, text, command, side):
        button = tk.Button(self.base, text=text, command=command)
        button.pack(side=side)
        return button
