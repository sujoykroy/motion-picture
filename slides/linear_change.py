class LinearChange:
    def __init__(self, start_value, end_value):
        self.start_value = start_value
        self.end_value = end_value

    def get_vlaue_at(self, frac):
        return self.start_value + (self.end_value - self.start_value)*frac