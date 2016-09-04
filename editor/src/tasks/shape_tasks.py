from ..shapes import get_hierarchy_names, get_shape_at_hierarchy
from ..commons import OrderedDict
from ..commons.misc import copy_list

class ShapeStateTask(object):
    NON_COMMUTATIVE_PROP_NAMES = ["anchor_at",
            "scale_x", "scale_y", "child_scale_x", "child_scale_y",
            "width", "height", "angle", "translation"]
    COMMUTATIVE_PROP_NAMES = ["border_color", "border_width", "fill_color",
                              "curves", "polygons"]

    def __init__(self, doc, shape, exclude_commutative=False):
        self.prev_shape_state = self.get_shape_state(doc, shape, exclude_commutative=exclude_commutative)
        self.post_shape_state = None
        doc.reundo.add_task(self)

    def save(self, doc, shape):
        self.post_shape_state = self.get_shape_state(doc, shape)

    def undo(self, doc):
        self.set_shape_state(doc, self.prev_shape_state)

    def redo(self, doc):
        if not self.post_shape_state: return
        self.set_shape_state(doc, self.post_shape_state)

    def remove(self, doc):
        doc.reundo.remove_task(self)

    @classmethod
    def get_shape_state(cls, doc, shape, exclude_commutative=False):
        shape_names = get_hierarchy_names(shape)
        shapes_props = OrderedDict()
        last_shape = None
        for i in range(len(shape_names)):
            shape_name = shape_names[i]
            if i == 0:
                last_shape = doc.main_multi_shape
                if last_shape.get_name() != shape_name:
                    last_shape = None
                    break
            else:
                last_shape = last_shape.shapes.get_item_by_name(shape_name)
                if last_shape is None:
                    break

            props = dict()
            cls.save_props(props, last_shape, cls.NON_COMMUTATIVE_PROP_NAMES)
            shapes_props.add(shape_name, props)
        if last_shape is not None and not exclude_commutative:
            cls.save_props(shapes_props[shape.get_name()], shape, cls.COMMUTATIVE_PROP_NAMES)
        return shapes_props

    @classmethod
    def set_shape_state(cls, doc, shapes_props):
        for i in range(len(shapes_props.keys)):
            shape_name = shapes_props.keys[i]
            if i == 0:
                last_shape =  doc.main_multi_shape
                if last_shape.get_name() != shape_name:
                    break
            else:
                last_shape = last_shape.shapes.get_item_by_name(shape_name)
                if last_shape is None:
                    break
            props = shapes_props.get_item_at_index(i)
            for prop_name in props.keys():
                if not hasattr(last_shape, prop_name): continue
                prop_value = props[prop_name]
                shape_prop = getattr(last_shape, prop_name)
                if type(prop_value) is list:
                    prop_value = copy_list(prop_value)

                if hasattr(shape_prop, "copy_from"):
                    shape_prop.copy_from(prop_value)
                else:
                    setattr(last_shape, prop_name, prop_value)

    @staticmethod
    def save_props(props, shape, prop_names):
        for prop_name in prop_names:
            if not hasattr(shape, prop_name): continue
            prop_value = getattr(shape, prop_name)
            if type(prop_value) is list:
                prop_value = copy_list(prop_value)
            elif hasattr(prop_value, "copy"):
                prop_value = prop_value.copy()
            props[prop_name] = prop_value

class ShapeDeleteTask(ShapeStateTask):
    def __init__(self, doc, shape):
        ShapeStateTask.__init__(self, doc, shape)
        self.hierarchy_names = get_hierarchy_names(shape)
        self.shape = shape

    def save(self, doc, parent_shape):
        self.post_shape_state = self.get_shape_state(doc, parent_shape, exclude_commutative=True)

    def undo(self, doc):
        parent_shape = get_shape_at_hierarchy(doc.main_multi_shape, self.hierarchy_names[0:-1])
        if not parent_shape: return
        parent_shape.add_shape(self.shape)
        self.set_shape_state(doc, self.prev_shape_state)

    def redo(self, doc):
        if not self.post_shape_state: return
        parent_shape = get_shape_at_hierarchy(doc.main_multi_shape, self.hierarchy_names[0:-1])
        if not parent_shape: return
        parent_shape.remove_shape(self.shape)
        self.set_shape_state(doc, self.post_shape_state)

class ShapeAddTask(ShapeStateTask):
    def __init__(self, doc, parent_shape):
        ShapeStateTask.__init__(self, doc, parent_shape, exclude_commutative=True)
        self.shape = None
        self.hierarchy_names = None

    def save(self, doc, shape):
        self.post_shape_state = self.get_shape_state(doc, shape)
        self.shape = shape
        self.hierarchy_names = get_hierarchy_names(shape)

    def undo(self, doc):
        parent_shape = get_shape_at_hierarchy(doc.main_multi_shape, self.hierarchy_names[0:-1])
        if not parent_shape: return
        parent_shape.remove_shape(self.shape)
        self.set_shape_state(doc, self.prev_shape_state)

    def redo(self, doc):
        if not self.post_shape_state: return
        parent_shape = get_shape_at_hierarchy(doc.main_multi_shape, self.hierarchy_names[0:-1])
        if not parent_shape: return
        parent_shape.add_shape(self.shape)
        self.set_shape_state(doc, self.post_shape_state)
