import tkinter as tk
import tkinter.ttk as ttk

from .frame import Frame

class ParamWidget:
    def __init__(self, master, effect_param, default):
        self._effect = None
        self._default = default
        self._effect_param = effect_param
        self._value_setter = None

        value_widget = None
        if effect_param.choices:
            value_widget = ttk.Combobox(master)
            for choice in effect_param.choices:
                value_widget.insert(tk.END, choice)
            value_widget.bind("<<ComboboxSelected>>", self._on_combo_change)
            self._value_setter = self._update_combo_value
        else:
            value_widget = ttk.Entry(master)
            value_widget.var = tk.StringVar()
            value_widget.var.trace('w', self._on_entry_change)
            value_widget['textvariable'] = value_widget.var
            self._value_setter = self._update_entry_value

        self.label = tk.Label(master, text=effect_param.name)
        self.value_widget = value_widget

    @property
    def default(self):
        return self._default

    @property
    def param_name(self):
        return self._effect_param.name

    def set_effect(self, effect):
        self._effect = effect
        if effect:
            value = effect.get_param(self._effect_param.name)
        else:
            value = self._default

        if self._value_setter:
            self._value_setter(value)

    def set_enabled(self, enable):
        if enable:
            self.value_widget['state' ] = tk.NORMAL
        else:
            self.value_widget['state' ] = tk.DISABLED

    def _update_combo_value(self, value):
        self.value_widget.set(value)

    def _on_combo_change(self):
        if not self._effect:
            return
        self._effect.set_param(
            self._effect_param.name,
            self._effect_param.parse(self.value_widget.get()))

    def _update_entry_value(self, value):
        self.value_widget.var.set(value)

    def _on_entry_change(self, *_):
        if not self._effect:
            return
        self._effect.set_param(
            self._effect_param.name, self.value_widget.var.get())

class EffectFrame(Frame):
    def __init__(self, master, effect_config, command):
        super().__init__(master)
        self._effect = None
        self._command = command
        self.effect_config = effect_config

        self._effect_var = tk.IntVar()
        self.widgets.check_button = tk.Checkbutton(
            self.base, text=effect_config.effect_name,
            variable=self._effect_var, command=self._on_checked)
        self.widgets.check_button.grid(row=0, column=0)

        effect_klass = effect_config.effect_class
        row = 1
        self._param_widgets = []
        for effect_param in effect_klass.PARAMS:
            param_widget = ParamWidget(
                self.base, effect_param,
                effect_config.defaults.get(effect_param.name))
            param_widget.label.grid(row=row, column=0)
            if param_widget.value_widget:
                param_widget.value_widget.grid(row=row, column=1)
            self._param_widgets.append(param_widget)
            row += 1

    @property
    def checked(self):
        return bool(self._effect_var.get())

    @checked.setter
    def checked(self, value):
        self._effect_var.set(int(value))
        self._set_widgets_enable(value)

    def _set_widgets_enable(self, value):
        for param_widget in self._param_widgets:
            param_widget.set_enabled(value)

    def _on_checked(self):
        self._set_widgets_enable(self.checked)
        self._command()

    def set_effect(self, effect):
        self._effect = effect
        for param_widget in self._param_widgets:
            param_widget.set_effect(effect)

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
