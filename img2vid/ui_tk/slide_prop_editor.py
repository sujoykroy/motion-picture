import tkinter as tk
import tkinter.scrolledtext as tkscrolledtext

from .frame import Frame
from .dialog import Dialog

from ..slides import ImageSlide, TextSlide

class SlidePropEditor(Frame):
    def __init__(self, master, app_config):
        super().__init__(
            master=master,
            app_config=app_config,
            event_names=["slide_updated", "crop_slide", "delete_slide"]
        )
        self._slide = None

        self.widgets.text_label = self._create_label("Caption")
        self.widgets.text = tkscrolledtext.ScrolledText(
            self.base, height="5", width="40")
        self.widgets.text.pack()
        self.widgets.text.bind("<KeyRelease>", self._text_changed)

        self.widgets.align_label = self._create_label("Alignment")
        self.widgets.align_list = tk.Listbox(self.base, height=5)
        for alignment in ImageSlide.CAP_ALIGNMENTS:
            self.widgets.align_list .insert(tk.END, alignment)
        self.widgets.align_list.bind("<ButtonRelease-1>", self._text_align_changed)
        self.widgets.align_list.pack()

        self.widgets.apply_button = self._create_button(
            "Apply", self._apply_slide_change, None)

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
        self.widgets.text.delete("1.0", tk.END)
        self.widgets.align_list.selection_clear(0, tk.END)
        for check_button in self.widgets.effect_checks.values():
            check_button.effect_var.set(0)

        self._slide = slide
        if not self._slide:
            return
        if isinstance(self._slide, TextSlide):
            align_state = tk.DISABLED
            self.widgets.text_label["text"] = "Text"
        else:
            align_state = tk.NORMAL
            self.widgets.text_label["text"] = "Caption"
            align_index = ImageSlide.CAP_ALIGNMENTS.index(self._slide.cap_align)
            self.widgets.align_list.selection_set(align_index)

        self.widgets.apply_button["state"] = align_state
        self.widgets.crop_button["state"] = align_state
        self.widgets.align_label["state"] = align_state
        self.widgets.align_list["state"] = align_state

        self.widgets.text.insert(tk.END, self._slide.text)
        for effect_name in self._slide.effects:
            check_button = self.widgets.effect_checks.get(effect_name)
            if check_button:
                check_button.effect_var.set(1)

    def _text_changed(self, _event):
        if not self._slide:
            return
        text = self.widgets.text.get(1.0, tk.END)
        self._slide.text = text
        if isinstance(self._slide, TextSlide):
            self.events.slide_updated.fire()

    def _apply_slide_change(self):
        self.events.slide_updated.fire()

    def _text_align_changed(self, _event):
        if not self._slide:
            return
        sel = self.widgets.align_list.curselection()
        if sel:
            align = ImageSlide.CAP_ALIGNMENTS[sel[0]]
            self._slide.cap_align = align

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

    def _create_label(self, text, pady=0):
        label = tk.Label(self.base, text=text)
        label.pack(pady=pady)
        return label

    def _create_button(self, text, command, side):
        button = tk.Button(self.base, text=text, command=command)
        button.pack(side=side)
        return button
