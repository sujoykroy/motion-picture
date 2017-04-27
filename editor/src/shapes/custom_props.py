from ..commons import *

class CustomPropLinkedTo(object):
    def __init__(self, shape, prop_name):
        self.shape = shape
        self.prop_name = prop_name

    def copy(self):
        return CustomPropLinkedTo(self.shape, self.prop_name)

    def get_id_name(self):
        return self.shape.get_name() + self.prop_name

    def __eq__(self, other):
        return isinstance(other, CustomPropLinkedTo) and \
               self.get_id_name() == other.get_id_name()

    def set_prop_value(self, value):
        self.shape.set_prop_value(self.prop_name, value)

class CustomProp(object):
    PropTypes = dict(point=0, text=1, color=2, font=3, number=4)

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

    def __init__(self, prop_name, prop_type):
        self.prop_name = prop_name
        self.prop_type = prop_type
        self.prop_value = self.get_default_value_for(prop_type)
        self.linked_to_items = []

    def copy(self):
        newob = CustomProp(self.prop_name, self.prop_type)
        newob.prop_value = copy_value(self.prop_value)
        for linked_to in self.linked_to_items:
            newob.linked_to_items.append(linked_to.copy())
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
    def __init__(self):
        self.props = OrderedDict()

    def copy(self):
        newob = CustomProps()
        for prop_name in self.props.keys:
            newob.props.add(prop_name, self.props[prop_name].copy())
        return newob

    def add_prop(self, prop_name, prop_type):
        if not self.props.key_exists(prop_name):
            prop_type = CustomProp.PropTypes[prop_type]
            custom_prop = CustomProp(prop_name, prop_type)
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



