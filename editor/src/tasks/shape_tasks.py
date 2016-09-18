from ..shapes import get_hierarchy_names, MultiSelectionShape
from ..commons import OrderedDict
from ..commons.misc import copy_list, Matrix
import cairo

class ShapeState(object):
    NON_COMMUTATIVE_PROP_NAMES = ["anchor_at",
            "scale_x", "scale_y", "post_scale_x", "post_scale_y",
            "width", "height", "angle", "pre_matrix", "translation", "shapes"]
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
                shape = shape.copy(copy_name=True)
                for leaf_shape_name in list(shape.shapes.names):
                    leaf_shape = shape.shapes[leaf_shape_name]
                    shape.remove_shape(leaf_shape, resize=False)

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
            props = self.ancestral_shapes_props.get_item_at_index(i)
            self.apply_props(props, last_shape)

        #when the topmost shape is the leaf shape
        if not self.ancestral_shapes_props.keys and self.leaf_shapes_props.keys:
            shape = doc.main_multi_shape
            shape_name = self.leaf_shapes_props.keys[0]
            if shape.get_name() == shape_name:
                props = self.leaf_shapes_props[shape_name]
                self.apply_props(props, shape)

        if last_shape:
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

    def get_leaf_shapes(self, doc):
        shapes = []
        for shape_name in self.leaf_shapes_props.keys:
            hierarchy = list(self.ancestral_shapes_props.keys) + [shape_name]
            if len(hierarchy) == 1:
                if doc.main_multi_shape.get_name() == shape_name:
                    shapes.append(doc.main_multi_shape)
                break
            shape = get_shape_at_hierarchy(doc.main_multi_shape, hierarchy)
            shapes.append(shape)
        return shapes

    @classmethod
    def apply_props(cls, props, shape):
        for prop_name in props.keys():
            if not hasattr(shape, prop_name): continue
            prop_value = props[prop_name]
            shape_prop = getattr(shape, prop_name)
            if type(prop_value) is list:
                prop_value = copy_list(prop_value)
            elif isinstance(prop_value, cairo.Matrix):
                prop_value = Matrix.copy(prop_value)

            if prop_name == "shapes":
                for child_shape_name in prop_value.keys:
                    child_shape_props = prop_value[child_shape_name]
                    child_shape = shape.shapes.get_item_by_name(child_shape_name)
                    if not child_shape:
                        continue
                    cls.apply_props(child_shape_props, child_shape)
            elif prop_name in ("polygons", "curves"):
                setattr(shape, prop_name, copy_list(prop_value))
            elif hasattr(shape_prop, "copy_from"):
                shape_prop.copy_from(prop_value)
            else:
                setattr(shape, prop_name, prop_value)

    @classmethod
    def save_props(cls, props, shape, prop_names):
        for prop_name in prop_names:
            if not hasattr(shape, prop_name): continue
            prop_value = getattr(shape, prop_name)
            if prop_name == "shapes":
                prop_value = OrderedDict()
                for child_shape in shape.shapes:
                    child_shape_props = dict()
                    cls.save_props(child_shape_props, child_shape, cls.NON_COMMUTATIVE_PROP_NAMES)
                    cls.save_props(child_shape_props, child_shape, cls.COMMUTATIVE_PROP_NAMES)
                    prop_value.add(child_shape.get_name(), child_shape_props)
            elif type(prop_value) is list:
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
        ShapeStateTask.__init__(self, doc, shape.parent_shape, is_leaf=False)
        self.deleted_shapes = []
        if isinstance(shape, MultiSelectionShape):
            for selected_shape in shape.shapes:
                self.deleted_shapes.append(selected_shape)
        else:
            self.deleted_shapes.append(shape)

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

class ShapeCombineTask(ShapeStateTask):
    def __init__(self, doc, shape):
        ShapeStateTask.__init__(self, doc, shape)
        self.deleted_shapes = []
        for child_shape in shape.shapes:
            self.deleted_shapes.append(child_shape)
        self.combined_shape = None

    def save(self, doc, new_shape):
        self.post_shape_state = ShapeState(doc, new_shape)
        self.combined_shape = new_shape

    def undo(self, doc):
        if not self.combined_shape: return
        parent_shape = self.prev_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        parent_shape.remove_shape(self.combined_shape)
        for deleted_shape in self.deleted_shapes:
            parent_shape.add_shape(deleted_shape)
        self.prev_shape_state.apply_shapes_state(doc)

    def redo(self, doc):
        if not self.combined_shape: return
        parent_shape = self.post_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        for deleted_shape in self.deleted_shapes:
            parent_shape.remove_shape(deleted_shape)
            deleted_shape.parent_shape = self.combined_shape
        parent_shape.add_shape(self.combined_shape)
        self.post_shape_state.apply_shapes_state(doc)

class MultiShapeBreakTask(ShapeStateTask):
    def __init__(self, doc, shape):
        ShapeStateTask.__init__(self, doc, shape)
        self.freed_shapes = []
        for child_shape in shape.shapes:
            self.freed_shapes.append([child_shape, child_shape.get_name(), None])
        self.orig_mega_shape = shape

    def save(self, doc, shape):
        self.post_shape_state = ShapeState(doc, shape)
        for i in range(len(self.freed_shapes)):
            self.freed_shapes[i][2] = self.freed_shapes[i][0].get_name()

    def undo(self, doc):
        parent_shape = self.prev_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        parent_shape.add_shape(self.orig_mega_shape)
        for freed_shape, old_name, new_name in self.freed_shapes:
            parent_shape.remove_shape(freed_shape)
            freed_shape.rename(old_name)
            self.orig_mega_shape.add_shape(freed_shape)
        self.prev_shape_state.apply_shapes_state(doc)

    def redo(self, doc):
        parent_shape = self.post_shape_state.get_leaf_shapes(doc)[0]
        if not parent_shape: return
        for freed_shape, old_name, new_name in self.freed_shapes:
            self.orig_mega_shape.remove_shape(freed_shape)
            freed_shape.rename(new_name)
            parent_shape.add_shape(freed_shape)
        parent_shape.remove_shape(self.orig_mega_shape)
        self.post_shape_state.apply_shapes_state(doc)

class ShapeMergeTask(ShapeStateTask):
    def __init__(self, doc, shape, merged_shapes):
        ShapeStateTask.__init__(self, doc, shape)
        self.merged_shapes = list(merged_shapes)

    def save(self, doc, mega_shape):
        self.post_shape_state = ShapeState(doc, mega_shape)

    def undo(self, doc):
        parent_shape = self.prev_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        for merged_shape in self.merged_shapes:
            parent_shape.add_shape(merged_shape)
        self.prev_shape_state.apply_shapes_state(doc)

    def redo(self, doc):
        if not self.post_shape_state: return
        parent_shape = self.post_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        for merged_shape in self.merged_shapes:
            parent_shape.remove_shape(merged_shape)
        self.post_shape_state.apply_shapes_state(doc)

class ShapeConvertTask(ShapeStateTask):
    def __init__(self, doc, old_shape):
        ShapeStateTask.__init__(self, doc, old_shape)
        self.old_shape = old_shape
        self.new_shape = None

    def save(self, doc, new_shape):
        self.post_shape_state = ShapeState(doc, new_shape)
        self.new_shape = new_shape

    def undo(self, doc):
        parent_shape = self.prev_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        parent_shape.remove_shape(self.new_shape)
        parent_shape.add_shape(self.old_shape)
        self.prev_shape_state.apply_shapes_state(doc)

    def redo(self, doc):
        if not self.post_shape_state: return
        parent_shape = self.post_shape_state.get_parent_shape(doc)
        if not parent_shape: return
        parent_shape.add_shape(self.new_shape)
        parent_shape.remove_shape(self.old_shape)
        self.post_shape_state.apply_shapes_state(doc)
