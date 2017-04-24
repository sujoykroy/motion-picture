from ..commons import Threshold, Text
import numpy, parser

class Freq(object):
    def __init__(self, start, end):
        start = Text.parse_number(start)
        end = Text.parse_number(end)
        if start<end:
            self.start = start
            self.end = end
        else:
            self.start = end
            self.end = start

    @classmethod
    def create_from_text(cls, text):
        arr = text.split(",")
        freqs = []
        for item in arr:
            item=item.strip()
            if not item:
                continue
            freq_values = item.split("-")
            if len(freq_values)!=2:
                continue
            freqs.append(Freq(*freq_values))
        return freqs

class FreqBand(object):
    def __init__(self, freqs, negate=False, mult=1., thresholds=None, cond_bands=None):
        self.freqs = []
        if isinstance(freqs, list):
            if len(freqs)==2 and type(freqs[0]) in (int, float):
                self.freqs.append(Freq(*freqs))
            else:
                for freq_span in freqs:
                    if isinstance(freq_span, str):
                        self.freqs.extend(Freq.create_from_text(freq_span))
                    elif isinstance(freq_span, list) and len(freq_span)==2:
                        self.freqs.append(Freq(*freq_span))
        elif isinstance(freqs, str):
            self.freqs.extend(Freq.create_from_text(freqs))
        self.negate = negate
        if isinstance(mult, str):
            mult = parser.expr(mult).compile()
        self.mult = mult
        self.thresholds = Threshold.parse(thresholds)
        self.cond_bands = cond_bands

