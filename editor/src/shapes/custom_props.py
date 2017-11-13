from ..commons import *
from xml.etree.ElementTree import Element as XmlElemen

class CustomPropLinkedTo(object):
    def __init__(self, shape, prop_name):
        self.shape = shape
        self.prop_name = prop_name

    def copy(self, parent_shape):
        shape = parent_shape.get_interior_shape(self.shape.get_name())
        return CustomPropLinkedTo(shape, self.prop_name)

    def get_id_name(self):
        return self.shape.get_name() + self.prop_name

    def __eq__(self, other):
        return isinstance(other, CustomPropLinkedTo) and \
               self.get_id_name() == other.get_id_name()

    def set_prop_value(self, value):
        self.shape.set_prop_value(self.prop_name, value)

class CustomProp(object):
    TAG_NAME = "cusprop"
    LINKED_TO_TAG_NAME = "linked_to"
    PropTypes = dict(point=0, text=1, color=2, font=3, number=4, int=5, file=6)

    @classmethod
    def get_default_value_for(cls, prop_type):
        if prop_type == cls.PropTypes["point"]:
            return Point(0, 0)
        elif prop_type == cls.PropTypes["text"]:
            return ""
        elif prop_type == cls.PropTypes["color"]:
            return Color.from_html("000000")
        elif prop_type == cls.PropTypes["font"]:
            return "8"
        elif prop_type == cls.PropTypes["number"]:
            return 1.
        elif prop_type == cls.PropTypes["int"]:
            return 1
        return None

    def __init__(self, prop_name, prop_type, extras=None):
        self.prop_name = prop_name
        self.prop_type = prop_type
        self.prop_value = self.get_default_value_for(prop_type)
        self.extras = extras
        self.linked_to_items = []

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["name"] = self.prop_name
        elm.attrib["type"] = "{0}".format(self.prop_type)
        if hasattr(self.prop_value, "to_text"):
            prop_value_str = self.prop_value.to_text()
        else:
            prop_value_str = "{0}".format(self.prop_value)
        elm.attrib["value"] = prop_value_str
        for linked_to in self.linked_to_items:
            linked_to_elm = XmlElement(self.LINKED_TO_TAG_NAME)
            linked_to_elm.attrib["shape"] = linked_to.shape.get_name()
            linked_to_elm.attrib["prop"] = linked_to.prop_name
            elm.append(linked_to_elm)
        return elm

    @classmethod
    def create_from_xml(cls, elm, shape):
        prop_name = elm.attrib["name"]
        prop_type = int(elm.attrib["type"])
        prop_value = elm.attrib["value"]
        if prop_type == cls.PropTypes["point"]:
            prop_value = Point.from_text(prop_value)
        elif prop_type == cls.PropTypes["color"]:
            prop_value = color_from_text(prop_value)
        elif prop_type == cls.PropTypes["number"]:
            prop_value = Text.parse_number(prop_value)
        newob = cls(prop_name, prop_type)
        newob.prop_value = prop_value
        for linked_to_elm in elm.findall(cls.LINKED_TO_TAG_NAME):
            linked_shape = linked_to_elm.attrib["shape"]
            linked_shape = shape.get_interior_shape(linked_shape)
            if not linked_shape:
                continue
            newob.add_linked_to(linked_shape, linked_to_elm.attrib["prop"])
        return newob

    def copy(self, parent_shape):
        newob = CustomProp(self.prop_name, self.prop_type)
        newob.prop_value = copy_value(self.prop_value)
        for linked_to in self.linked_to_items:
            newob.linked_to_items.append(linked_to.copy(parent_shape))
        return newob

    @classmethod
    def can_insert_time_slice(cls, prop_type):
        if prop_type in (cls.PropType["point"], cls.PropType["number"]):
            return True
        return False

    def add_linked_to(self, shape, prop_name):
        if not self.get_linked_to(shape, prop_name):
            self.linked_to_items.append(CustomPropLinkedTo(shape, prop_name))

    def remove_linked_to(self, shape, prop_name):
        item = self.get_linked_to(shape, prop_name)
        if item:
            self.linked_to_items.remove(item)

    def get_linked_to(self, shape, prop_name):
        for linked_to in self.linked_to_items:
            if linked_to.shape == shape and linked_to.prop_name == prop_name:
                return linked_to
        return None

    def set_prop_value(self, prop_value):
        if self.prop_type == self.PropTypes["color"]:
            prop_value = Color.parse(prop_value)
        self.prop_value = prop_value
        for linked_to_item in self.linked_to_items:
            linked_to_item.set_prop_value(prop_value)

    def get_prop_value(self):
        return self.prop_value

    def get_prop_type_name(self):
        for type_name, type_value in self.PropTypes.items():
            if type_value == self.prop_type:
                return type_name
        return None

class CustomProps(object):
    TAG_NAME = "cusprops"

    def __init__(self):
        self.props = OrderedDict()

    def clear(self):
        self.props.clear()

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        for custom_prop in self.props:
            elm.append(custom_prop.get_xml_element())
        return elm

    @classmethod
    def create_from_xml(cls, elm, shape):
        newob = cls()
        for prop_elm in elm.findall(CustomProp.TAG_NAME):
            custom_prop = CustomProp.create_from_xml(prop_elm, shape)
            if custom_prop:
                newob.props.add(custom_prop.prop_name, custom_prop)
        return newob

    def copy(self, parent_shape):
        newob = CustomProps()
        for prop_name in self.props.keys:
            newob.props.add(prop_name, self.props[prop_name].copy(parent_shape))
        return newob

    def add_prop(self, prop_name, prop_type, extras=None):
        if not self.props.key_exists(prop_name):
            prop_type = CustomProp.PropTypes[prop_type]
            custom_prop = CustomProp(prop_name, prop_type, extras)
            self.props.add(prop_name, custom_prop)

    def remove_prop(self, prop_name):
        self.props.remove(prop_name)

    def set_prop_value(self, prop_name, value):
        if not self.props.key_exists(prop_name):
            return
        self.props[prop_name].set_prop_value(copy_value(value))

    def get_prop_value(self, prop_name):
        if not self.props.key_exists(prop_name):
            return None
        return self.props[prop_name].get_prop_value()

    def get_prop(self, prop_name):
        return self.props[prop_name]

    def has_prop(self, prop_name):
        return self.props.key_exists(prop_name)

    def has_any_prop(self):
        return len(self.props)>0

    def apply_props(self):
        for custom_prop in self.props:
            custom_prop.set_prop_value(custom_prop.prop_value)
