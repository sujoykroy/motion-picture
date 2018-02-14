class DebugConfig:
    def __init__(self, **kwargs):
        self.params = kwargs

    @property
    def pan_trac(self):
        return self.params.get("pan_trac")
