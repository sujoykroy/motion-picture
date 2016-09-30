from xml.etree.ElementTree import Element as XmlElement
import math

class TimeChangeType(object):
    TAG_NAME = "time_change_type"
    TYPE_NAME = None

    def __init__(self):
        pass

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["type"] = self.TYPE_NAME
        return elm

    def copy(self):
        return TimeChangeType()

    def value_at(self, start_value, end_value, t, duration):
        return start_value + (end_value - start_value)*t/float(duration)

    def get_min_max_value(self, start_value, end_value, duration):
        return min(start_value, end_value), max(start_value, end_value)

class PeriodicChangeType(TimeChangeType):
    PHASE_NAME = "phase"
    AMPLITUDE_NAME = "amplitude"
    PERIOD_NAME = "period"

    def __init__(self,  amplitude, period, phase):
        self.period = float(period)
        self.phase = phase
        self.amplitude = amplitude

    def get_xml_element(self):
        elm = TimeChangeType.get_xml_element(self)
        elm.attrib[self.PHASE_NAME] = "{0}".format(self.phase)
        elm.attrib[self.AMPLITUDE_NAME] = "{0}".format(self.amplitude)
        elm.attrib[self.PERIOD_NAME] = "{0}".format(self.period)
        return elm

    def copy(self):
        return self.create_new_object(self.amplitude, self.period, self.phase)

    @classmethod
    def create_new_object(cls, amplitude, period, phase):
        return cls(amplitude, period, phase)

    @classmethod
    def create_from_xml_element(cls, elm):
        amplitude = float(elm.attrib.get(cls.AMPLITUDE_NAME, 1.))
        phase = float(elm.attrib.get(cls.PHASE_NAME, 0.))
        period = float(elm.attrib.get(cls.PERIOD_NAME, 1.))
        change_type = cls(amplitude, period, phase)
        return change_type

    def self_value_at(self, t):
        return 0

    def value_at(self, start_value, end_value, t, duration):
        value = TimeChangeType.value_at(self, start_value, end_value, t, duration)
        value += self.self_value_at(t)
        return value

    def get_min_max_value(self, start_value, end_value, duration):
        minv = min(start_value-self.amplitude, end_value-self.amplitude)
        maxv = max(start_value+self.amplitude, end_value+self.amplitude)
        return minv, maxv

class SineChangeType(PeriodicChangeType):
    TYPE_NAME = "sine"

    def self_value_at(self, t):
        value = self.amplitude*math.sin(math.pi*2*t/self.period + self.phase*math.pi/180.)
        return value


class TriangleChangeType(PeriodicChangeType):
    TYPE_NAME = "triangle"

    def self_value_at(self, t):
        frac = t/self.period
        frac += self.phase/360.
        frac %= 1
        if frac>.5: frac = 1-frac
        frac *= 2
        return self.amplitude*frac

class LoopChangeType(PeriodicChangeType):
    TYPE_NAME = "loop"

    def self_value_at(self, t):
        frac = t/self.period
        frac += self.phase/360.
        frac %= 1
        return self.amplitude*frac

