from xml.etree.ElementTree import Element as XmlElement
import math, numpy

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
        if isinstance(start_value, list):
            value = []
            for i in range(len(start_value)):
                value.append(start_value[i] + (end_value[i] - start_value[i])*t/float(duration))
            return value
        else:
            return start_value + (end_value - start_value)*t/float(duration)

    def get_min_max_value(self, start_value, end_value, duration):
        if isinstance(start_value, list):
            minv = None
            maxv = None
            for i in range(min(len(start_value), len(end_value))):
                minvl = min(start_value[i], end_value[i])
                maxvl = max(start_value[i], end_value[i])
                if minv is not  None:
                    minv = min(minvl, minv)
                else:
                    minv = minvl
                if minv is not  None:
                    maxv = max(maxvl, maxv)
                else:
                    maxv = maxvl
            return minv, maxv
        else:
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
        self_value = self.self_value_at(t)
        if isinstance(value, list):
            for i in range(len(value)):
                value[i] += self_value
        else:
            value = value + self_value
        return value

    def get_min_max_value(self, start_value, end_value, duration):
        if isinstance(start_value, list):
            minv = None
            maxv = None
            for i in range(len(start_value)):
                minvl = min(start_value[i]-self.amplitude, end_value[i]-self.amplitude)
                maxvl = max(start_value[i]+self.amplitude, end_value[i]+self.amplitude)
                if minv is not  None:
                    minv = min(minvl, minv)
                else:
                    minv = minvl
                if minv is not  None:
                    maxv = max(maxvl, maxv)
                else:
                    maxv = maxvl
            return minv, maxv
        else:
            minv = min(start_value-self.amplitude, end_value-self.amplitude)
            maxv = max(start_value+self.amplitude, end_value+self.amplitude)
        return minv, maxv

class SineChangeType(PeriodicChangeType):
    TYPE_NAME = "sine"

    def self_value_at(self, t):
        if isinstance(t, numpy.ndarray):
            value = self.amplitude*numpy.sin(math.pi*2*t/self.period + self.phase*math.pi/180.)
        else:
            value = self.amplitude*math.sin(math.pi*2*t/self.period + self.phase*math.pi/180.)
        return value


class TriangleChangeType(PeriodicChangeType):
    TYPE_NAME = "triangle"

    def self_value_at(self, t):
        frac = t/self.period
        frac = frac + self.phase/360.
        frac = frac % 1
        if isinstance(frac, numpy.ndarray):
            frac = numpy.where(frac>.5, 1-frac, frac)
        else:
            if frac>.5: frac = 1-frac
        frac = frac * 2
        return self.amplitude*frac

class LoopChangeType(TimeChangeType):
    TYPE_NAME = "loop"
    LOOP_COUNT_NAME = "count"

    def __init__(self, loop_count=1.0):
        self.loop_count = loop_count

    def value_at(self, start_value, end_value, t, duration):
        loop_duration = duration/(1.0*self.loop_count)
        t = t % loop_duration
        return super(LoopChangeType, self).value_at(start_value, end_value, t, loop_duration)

    def get_xml_element(self):
        elm = super(LoopChangeType, self).get_xml_element()
        elm.attrib[self.LOOP_COUNT_NAME] = "{0}".format(self.loop_count)
        return elm

    def copy(self):
        return LoopChangeType(self.loop_count)

    @classmethod
    def create_from_xml_element(cls, elm):
        loop_count = int(float(elm.attrib.get(cls.LOOP_COUNT_NAME, 1.)))
        change_type = cls(loop_count)
        return change_type
