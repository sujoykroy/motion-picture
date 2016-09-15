from ..shapes import get_hierarchy_names, MultiSelectionShape
from ..commons import OrderedDict
from ..commons.misc import copy_list, Matrix
import cairo

class ShapeState(object):
    NON_COMMUTATIVE_PROP_NAMES = ["anchor_at",
            "scale_x", "scale_y", "post_scale_x", "post_scale_y",
            "width", "height", "angle", "pre_matrix", "translation"]
    COMMUTATIVE_PROP_NAMES = ["border_color", "border_width", "fill_color",
                              "curves", "polygons"]

    def __init__(self, doc, shape, is_leaf=True):
        self.ancestral_shapes_props = OrderedDict()
        self.leaf_shapes_props = OrderedDict()

        if is_leaf:
            ancestral_names = get_hierarchy_names(shape.parent_shape)
        else:
            ancestral_names = get_hierarchy_names(shape)

        last_shape = None
        for i in range(len(ancestral_names)):
            shape_name = ancestral_names[i]
            if i == 0:
                last_shape = doc.main_multi_shape
                if last_shape.get_name() != shape_name:
                    last_shape = None
                    break
            else:
                last_shape = last_shape.shapes.get_item_by_name(shape_name)
                if last_shape is None:
                    if isinstance(last_shape, MultiShape):
                        for child_shape in last_shape.shapes:
                            if not isinstance(child_shape, MultiSelectionShape):
                                continue
                            last_shape = child_shape.shapes.get_item_by_name(shape_name)
                            break
                if last_shape is None:
                    break
            props = dict()
            self.save_props(props, last_shape, self.NON_COMMUTATIVE_PROP_NAMES)
            self.ancestral_shapes_props.add(shape_name, props)

        if is_leaf:
            if isinstance(shape, MultiSelectionShape):
                for leaf_shape in shape.shapes:
                    props = dict()
                    self.save_props(props, leaf_shape, self.NON_COMMUTATIVE_PROP_NAMES)
                    self.save_props(props, leaf_shape, self.COMMUTATIVE_PROP_NAMES)
                    self.leaf_shapes_props.add(leaf_shape.get_name(), props)
            else:
                props = dict()
                self.save_props(props, shape, self.NON_COMMUTATIVE_PROP_NAMES)
                self.save_props(props, shape, self.COMMUTATIVE_PROP_NAMES)
                self.leaf_shapes_props.add(shape.get_name(), props)

    def apply_shapes_state(self, doc):
        for i in range(len(self.ancestral_shapes_props.keys)):
            shape_name = self.ancestral_shapes_props.keys[i]
            if i == 0:
                last_shape = doc.main_multi_shape
                if last_shape.get_name() != shape_name:
                    break
            else:
                last_shape = last_shape.shapes.get_item_by_name(shape_name)
                if last_shape is None:
                    break
            props = self.ancestral_shapes_props.get_item_at_index(i)
            self.apply_props(props, last_shape)

        for shape_name in self.leaf_shapes_props.keys:
            shape = last_shape.shapes.get_item_by_name(shape_name)
            if not shape: continue
            props = self.leaf_shapes_props[shape_name]
            self.apply_props(props, shape)

    def get_parent_shape(self, doc):
        last_shape = None
        for i in range(len(self.ancestral_shapes_props.keys)):
            shape_name = self.ancestral_shapes_props.keys[i]
            if i == 0:
                last_shape = doc.main_multi_shape
                if last_shape.get_name() != shape_name:
                    break
            else:
                last_shape = last_shape.shapes.get_item_by_name(shape_name)
                if last_shape is None:
                    break
        return last_shape

    @staticmethod
    def apply_props(props, shape):
        for prop_name in props.keys():
            if not hasattr(shape, prop_name): continue
            prop_value = props[prop_name]
            shape_prop = getattr(shape, prop_name)
            if type(prop_value) is list:
                prop_value = copy_list(prop_value)
            elif isinstance(prop_value, cairo.Matrix):
                prop_value = Matrix.copy(prop_value)
            if hasattr(shape_prop, "copy_from"):
                shape_prop.copy_from(prop_value)
            else:
                setattr(shape, prop_name, prop_value)

    @staticmethod
    def save_props(props, shape, prop_names):
        for prop_name in prop_names:
            if not hasattr(shape, prop_name): continue
            prop_value = getattr(shape, prop_name)
            if type(prop_value) is list:
                prop_value = copy_list(prop_value)
            elif isinstance(prop_value, cairo.Matrix):
                prop_value = Matrix.copy(prop_value)
            elif hasattr(prop_value, "copy"):
                prop_value = prop_value.copy()
            props[prop_name] = prop_value

class ShapeStateTask(object):
    def __init__(self, doc, shape, is_leaf=True):
        self.prev_shape_state = ShapeState(doc, shape, is_leaf)
        self.post_shape_state = None
        doc.reundo.add_task(self)

    def save(self, doc, shape):
        self.post_shape_state = ShapeState(doc, shape)

    def undo(self, doc):
        self.prev_shape_state.apply_shapes_state(doc)

    def redo(self, doc):
        if not self.post_shape_state: return
        self.post_shape_state.apply_shapes_state(doc)

    def remove(self, doc):
        doc.reundo.remove_task(self)

class ShapeDeleteTask(ShapeStateTask):
    def __init__(self, doc, shape):
        ShapeStateTask.__init__(self, doc, shape)
        self.deleted_shapes = []
        if isinstance(shape, MultiSelectionShape):
            for selected_shape in shape.shapes:
                self.deleted_shapes.append(selected_shape)

    def save(self, doc, parent_shape):
        self.post_shape_state = ShapeState(doc, parent_shape, is_leaf=False)

    def undo(self, doc):
        parent_shape = self.prev_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        for deleted_shape in self.deleted_shapes:
            parent_shape.add_shape(deleted_shape)
        self.prev_shape_state.apply_shapes_state(doc)

    def redo(self, doc):
        if not self.post_shape_state: return
        parent_shape = self.post_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        for deleted_shape in self.deleted_shapes:
            parent_shape.remove_shape(deleted_shape)
        self.post_shape_state.apply_shapes_state(doc)

class ShapeAddTask(ShapeStateTask):
    def __init__(self, doc, parent_shape):
        ShapeStateTask.__init__(self, doc, parent_shape, is_leaf=False)
        self.shape = None

    def save(self, doc, shape):
        self.post_shape_state = ShapeState(doc, shape)
        self.shape = shape

    def undo(self, doc):
        parent_shape = self.prev_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        parent_shape.remove_shape(self.shape)
        self.prev_shape_state.apply_shapes_state(doc)

    def redo(self, doc):
        if not self.post_shape_state: return
        parent_shape = self.post_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        parent_shape.add_shape(self.shape)
        self.post_shape_state.apply_shapes_state(doc)
