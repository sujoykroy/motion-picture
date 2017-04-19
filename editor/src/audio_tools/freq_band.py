from ..commons import Threshold

class FreqBand(object):
    def __init__(self, start_freq, end_freq, mult=1., thresholds=None, cond_bands=None):
        self.start_freq = start_freq
        self.end_freq = end_freq
        self.mult = mult
        self.thresholds = Threshold.parse(thresholds)
        self.cond_bands = cond_bands

