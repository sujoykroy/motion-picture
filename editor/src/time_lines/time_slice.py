from xml.etree.ElementTree import Element as XmlElement
from time_change_types import *

class TimeSlice(object):
    TAG_NAME = "time_slice"
    START_VALUE_NAME = "start_value"
    END_VALUE_NAME = "end_value"
    DURATION_NAME = "duration"
    PROP_DATA_TAG_NAME = "prop_data"
    LINKED_TO_NEXT_NAME = "linked"
    ID_SEED = 0
    def __init__(self,  start_value, end_value, duration, change_type=None, prop_data=None):
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        if change_type is None:
            change_type = TimeChangeType()
        self.change_type = change_type
        self.prop_data = prop_data
        self.id_num = TimeSlice.ID_SEED
        self.linked_to_next = False
        TimeSlice.ID_SEED += 1

    def __str__(self):
        return "TimeSlice[{3}], sv={0}, ev={1}, dur={2}".format(
                self.start_value, self.end_value, self.duration, self.id_num)

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib[self.START_VALUE_NAME] = "{0}".format(self.start_value)
        elm.attrib[self.END_VALUE_NAME] = "{0}".format(self.end_value)
        elm.attrib[self.DURATION_NAME] = "{0}".format(self.duration)
        elm.attrib[self.LINKED_TO_NEXT_NAME] = "{0}".format(self.linked_to_next)
        if type(self.change_type) is not TimeChangeType:
            elm.append(self.change_type.get_xml_element())
        if self.prop_data:
            for key, value in self.prop_data.items():
                if value is None: continue
                prop_data_elm = XmlElement(self.PROP_DATA_TAG_NAME)
                prop_data_elm.attrib["key"] = "{0}".format(key)
                prop_data_elm.attrib["value"] = "{0}".format(value)
                prop_data_elm.attrib["type"] = value.__class__.__name__
                elm.append(prop_data_elm)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        start_value = float(elm.attrib.get(cls.START_VALUE_NAME, 0.))
        end_value = float(elm.attrib.get(cls.END_VALUE_NAME, 1.))
        duration = float(elm.attrib.get(cls.DURATION_NAME, 1.))
        linked_to_next = elm.attrib.get(cls.LINKED_TO_NEXT_NAME, False)
        if linked_to_next == "True":
            linked_to_next = True
        else:
            linked_to_next = False
        change_type = None
        change_type_elm  = elm.find(TimeChangeType.TAG_NAME)
        if change_type_elm is not None:
            type_name = change_type_elm.attrib["type"]
            if type_name ==  SineChangeType.TYPE_NAME:
                change_type = SineChangeType.create_from_xml_element(change_type_elm)
            elif type_name ==  TriangleChangeType.TYPE_NAME:
                change_type = TriangleChangeType.create_from_xml_element(change_type_elm)
            elif type_name ==  LoopChangeType.TYPE_NAME:
                change_type = LoopChangeType.create_from_xml_element(change_type_elm)
        prop_data = None
        prop_data_elm_all = elm.findall(cls.PROP_DATA_TAG_NAME)
        if prop_data_elm_all:
            prop_data = dict()
            for prop_data_elm in prop_data_elm_all:
                key = prop_data_elm.attrib["key"]
                value = prop_data_elm.attrib["value"]
                value_type = prop_data_elm.attrib["type"]
                if value_type in ("float", "int"):
                    value = float(value)
                prop_data[key] = value
        time_slice = cls(start_value, end_value, duration, change_type, prop_data)
        time_slice.linked_to_next = linked_to_next
        return time_slice

    def __hash__(self):
        return hash(self.id_num)

    def __eq__(self, other):
        return isinstance(other, TimeSlice) and self.id_num == other.id_num

    def __ne__(self, other):
        return not (self == other)

    def set_change_type(self, change_type):
        self.change_type = change_type

    def value_at(self, t):
        return self.change_type.value_at(self.start_value, self.end_value, t, self.duration)

    def get_min_max_value(self):
        tmin, tmax = self.change_type.get_min_max_value(self.start_value, self.end_value, self.duration)
        return (tmin, tmax)

    def get_change_type_class(self):
        return type(self.change_type)

    def set_change_type_class(self, change_type_class):
        if change_type_class and change_type_class.TYPE_NAME == self.change_type.TYPE_NAME:
            return #don't change if already of this type
        if change_type_class in (SineChangeType, TriangleChangeType, LoopChangeType):
            self.change_type = change_type_class(
                    amplitude=self.end_value-self.start_value,
                    phase=0, period=self.duration)
        else:
            self.change_type = TimeChangeType()

