class TimeSlice:
    def __init__(self, slide):
        self.slide = slide
        self.duration = 0
        self.params_changes = dict()
        self.image = None

    def set_duration(self, duration):
        self.duration = duration

    def set_params_change(self, param_name, change_pattern):
        self.params_changes[param_name] = change_pattern
