import tkinter as tk

from .frame import Frame

class EffectFrame(Frame):
    def __init__(self, master, effect_config, command):
        super().__init__(master)

        self.effect_config = effect_config

        self._effect_var = tk.IntVar()
        self.widgets.check_button = tk.Checkbutton(
            self.base, text=effect_config.effect_name,
            variable=self._effect_var, command=command)
        self.widgets.check_button.grid(row=0, column=0)

    @property
    def checked(self):
        return bool(self._effect_var.get())

    @checked.setter
    def checked(self, value):
        self._effect_var.set(int(value))

    def set_effect(self, effect):
        pass

class EffectsPropEditor(Frame):
    def __init__(self, master, app_config):
        super().__init__(
            master=master,
            app_config=app_config,
            event_names=["effects_updated"]
        )
        self._slide = None
        self.widgets.effects = {}

        for effect_name in sorted(app_config.effects.keys()):
            effect_config = app_config.effects[effect_name]
            eff_frame = EffectFrame(
                self.base, effect_config, self._update_effects)
            eff_frame.pack(fill=tk.X)
            self.widgets.effects[effect_name] = eff_frame

    def set_slide(self, slide):
        self._slide = slide
        for eff_name, eff_frame in self.widgets.effects.items():
            if eff_name in slide.effects:
                eff_frame.checked = True
                eff_frame.set_effect(slide.effects[eff_name])
            else:
                eff_frame.checked = False
                eff_frame.set_effect(None)

    def _update_effects(self):
        if not self._slide:
            return
        for eff_name, eff_frame in self.widgets.effects.items():
            if eff_frame.checked:
                self._slide.add_effect(
                    eff_frame.effect_config.effect_class,
                    eff_frame.effect_config.defaults)
            else:
                self._slide.remove_effect(eff_name)
        self.events.effects_updated.fire()
