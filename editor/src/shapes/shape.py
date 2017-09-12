from ..commons import *
from ..commons.draw_utils import *
from gi.repository import Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
import time, cairo
from xml.etree.ElementTree import Element as XmlElement
from mirror import Mirror
from shape_list import ShapeList

class Shape(object):
    ID_SEED = 0
    TAG_NAME = "shape"
    POSE_SHAPE_TAG_NAME = "pose_shape"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        self.anchor_at = anchor_at
        self.border_color = Color.parse(border_color)
        self.border_width = border_width
        self.fill_color = Color.parse(fill_color)
        self.width = max(1, width)
        self.height= max(1, height)

        self.scale_x = 1.
        self.scale_y = 1.
        self.same_xy_scale = False
        self.post_scale_x = 1.
        self.post_scale_y = 1.
        self.translation = Point(0,0)
        self.angle = 0
        self.pre_matrix = None
        self.visible = True

        self.id_num = self.get_new_id()

        self.parent_shape = None
        self._name = self.new_name()

        self.moveable = True
        self.linked_to = None
        self.linked_clones = None
        self.border_dashes = None
        self.border_dash_offset = 0

        self.follow_curve = None
        self.followed_upto = 0.
        self.renderable = True

        self.locked_to_shape = None
        self.locked_shapes = None
        self.selectable = True
        self.has_outline = True
        self._locked_to = None

    @staticmethod
    def get_new_id():
        id_num = Shape.ID_SEED
        Shape.ID_SEED += 1
        return id_num

    def get_class_name(self):
        return self.__class__.__name__

    def can_resize(self):
        return self.moveable

    def can_rotate(self):
        return self.moveable

    def can_change_anchor(self):
        return self.moveable

    def has_poses(self):
        return False

    def init_locked_shapes(self):
        if self.locked_shapes is None:
            self.locked_shapes = ShapeList(unique=False)

    def set_followed_upto(self, value, prop_data=None):
        self.followed_upto = value
        if prop_data:
            curve_name = prop_data.get("follow_curve")
            if curve_name:
                self.follow_curve = curve_name
            follow_angle = prop_data.get("follow_angle")
        else:
            follow_angle = False
        if not self.follow_curve:
            return
        if self.parent_shape is None:
            return
        curve_shape = self.parent_shape.shapes.get_item_by_name(self.follow_curve)
        if not curve_shape or not hasattr(curve_shape, "baked_points"):
            return
        point, angle = curve_shape.get_baked_point(self.followed_upto)
        self.move_to(point.x, point.y)
        if follow_angle:
            self.set_angle(angle)

    def reset_transformations(self):
        self.scale_x = 1.
        self.scale_y = 1.
        self.post_scale_x = 1.
        self.post_scale_y = 1.
        self.translation = Point(0,0)
        self.angle = 0
        self.pre_matrix = None
        self.anchor_at.assign(0,0)

    def get_prop_type(self, prop_name):
        if prop_name == "xy":
            return "number_list"
        return "number"

    def cleanup(self):
        if self.linked_clones:
            for linked_clone in self.linked_clones:
                linked_clone.set_linked_to(None)
        if self.linked_to:
            self.set_linked_to(None)
        if self.locked_shapes:
            for locked_shape in self.locked_shapes:
                locked_shape.set_locked_to(None)
        if self.locked_to_shape:
            self.set_locked_to(None)
        if hasattr(self, "anchor_shape"):
            self.anchor_shape.cleanup()

    def set_linked_to(self, linked_to_shape):
        if self.linked_to:
            self.linked_to.remove_linked_clone(self)
        self.linked_to = linked_to_shape
        if linked_to_shape:
            linked_to_shape.add_linked_clone(self)

    def add_linked_clone(self, linked_clone):
        if self.linked_clones is None:
            self.linked_clones = []
        if linked_clone not in self.linked_clones:
            self.linked_clones.append(linked_clone)

    def remove_linked_clone(self, linked_clone):
        if self.linked_clones and linked_clone in self.linked_clones:
            self.linked_clones.remove(linked_clone)

    def copy_data_from_linked(self):
        if not self.linked_to: return
        self.border_color = copy_value(self.linked_to.border_color)
        self.border_width = copy_value(self.linked_to.border_width)
        self.fill_color = copy_value(self.linked_to.fill_color)
        self.width = self.linked_to.width
        self.height = self.linked_to.height

    def get_angle_post_scale_matrix(self):
        matrix = cairo.Matrix()
        matrix.rotate(self.angle*RAD_PER_DEG)
        matrix.scale(self.post_scale_x, self.post_scale_y)
        return matrix

    def get_interior_shapes(self):
        return None

    def get_interior_shape(self, shape_path):
        if not shape_path:
            return None
        shape = self
        if isinstance(shape_path, list):
            shape_names = shape_path
        else:
            shape_path = shape_path.strip()
            shape_path = shape_path.split("\\")
            shape_names = None
            for i in xrange(len(shape_path)):
                if shape_path[i] is '':
                    shape = shape.parent_shape
                else:
                    shape_names = shape_path[i].split(".")
                    break
            if shape is None:
                return None
        if not shape_names:
            return None
        interior_shapes = shape.get_interior_shapes()
        shape_name = shape_names[0]
        if shape_name == ANCHOR_SHAPE_NAME:
            shape = shape.get_anchor_shape()
        else:
            if not interior_shapes or not interior_shapes.contain(shape_name):
                return None
            shape = interior_shapes[shape_name]
        if len(shape_names)>1:
            return shape.get_interior_shape(shape_names[1:])
        return shape

    def get_shape_ancestors(self, root_shape=None, lock=False, include_root=False):
        shapes = []
        shape = self
        while True:
            if shape == root_shape:
                if include_root:
                    shapes.insert(0, shape)
                break
            shapes.insert(0, shape)
            if lock and shape.locked_to_shape:
                shape = shape.locked_to_shape
            else:
                shape = shape.parent_shape
            if shape is None:
                break
        return shapes

    def get_shape_path(self, root_shape=None):
        shapes = self.get_shape_ancestors(root_shape=root_shape, lock=False, include_root=True)
        shape_names = []
        ups = []
        if shapes and root_shape and shapes[0] != root_shape:
            rel_root_shape = root_shape
            while rel_root_shape:
                if rel_root_shape in shapes:
                    root_shape_index = shapes.index(rel_root_shape)
                    shapes = shapes[root_shape_index:]
                    break
                rel_root_shape = rel_root_shape.parent_shape
                if rel_root_shape:
                    ups.append("\\")
        ups = "".join(ups)
        for shape in shapes[1:]:
            shape_names.append(shape.get_name())
        return ups + (".".join(shape_names))

    def add_interior_shape(self, shape, shape_list, transform=True, lock=False):
        if shape_list.contain(shape): return
        if transform:
            shape_abs_anchor_at = shape.get_abs_anchor_at()
            """
            if self.locked_to_shape:
                rel_shape_abs_anchor_at = self.transform_locked_shape_point(
                    shape_abs_anchor_at, root_shape=shape.parent_shape)
                rel_shape_abs_anchor_at = self.transform_point(rel_shape_abs_anchor_at)
            else:
                rel_shape_abs_anchor_at = self.transform_point(shape_abs_anchor_at)
            rel_shape_abs_anchor_at = self.transform_locked_shape_point(
                            shape_abs_anchor_at, root_shape=shape.parent_shape)
            """
            rel_shape_abs_anchor_at = self.transform_locked_shape_point(
                    shape_abs_anchor_at,
                    root_shape=shape.get_active_parent_shape(),
                    exclude_last=False)
            shape.move_to(rel_shape_abs_anchor_at.x, rel_shape_abs_anchor_at.y)
            shape.set_angle(shape.get_angle()-self.get_angle())
        if lock:
            shape.locked_to_shape = self
        else:
            shape.parent_shape = self

        shape_list.add(shape)

    def remove_interior_shape(self, shape, shape_list, transform=True, lock=False):
        if not shape_list.contain(shape): return None

        if transform:
            abs_outline = shape.get_abs_outline(0)
            shape_abs_anchor_at = shape.get_abs_anchor_at()
            #old_translation_point = shape.translation.copy()
            #if lock:
            #    new_translation_point = self.reverse_transform_locked_shape_point(
            #        old_translation_point, root_shape=shape.get_active_parent_shape())
            #else:
            #    new_translation_point = self.reverse_transform_point(old_translation_point)
            angle = shape.get_angle()+self.get_angle()

        if lock:
            if transform:
                abs_anchor_at = self.reverse_transform_locked_shape_point(
                    shape_abs_anchor_at, root_shape=shape.parent_shape)
            if self == shape.locked_to_shape:
                shape.locked_to_shape = None
        else:
            if transform:
                abs_anchor_at = self.reverse_transform_point(shape_abs_anchor_at)
            if self == shape.parent_shape:
                shape.parent_shape = None

        if transform:
            if shape.pre_matrix:
                shape.prepend_pre_matrix(self.get_angle_post_scale_matrix())
            else:
                if self.get_angle()==0:
                    if abs(shape.get_angle())>0:
                        shape.scale_x *= self.post_scale_x
                        shape.scale_y *= self.post_scale_y
                    else:
                        shape.set_width(shape.width*self.post_scale_x, fixed_anchor=False)
                        shape.set_height(shape.height*self.post_scale_y, fixed_anchor=False)
                        shape.anchor_at.scale(self.post_scale_x, self.post_scale_y)
                else:
                    if self.post_scale_x != 1 or self.post_scale_y != 1:
                        shape.prepend_pre_matrix(self.get_angle_post_scale_matrix())
                    else:
                        shape.set_angle(angle)
            shape.move_to(abs_anchor_at.x, abs_anchor_at.y)

        shape_list.remove(shape)
        return shape

    def clear_pre_locked_to(self):
        self._locked_to=None

    def set_pre_locked_to(self, shape_name):
        self._locked_to=shape_name

    def build_locked_to(self, up=0):
        if self._locked_to and not self.locked_to_shape:
            up_parents = "\\"*(up+1)
            if up_parents and self._locked_to.find(up_parents)==0:
                return
            self.set_locked_to(self._locked_to, direct=True)
            self._locked_to = None

    def set_locked_to(self, shape_name, direct=False):
        if isinstance(shape_name, Shape) or not shape_name:
            locked_to_shape = shape_name
            if locked_to_shape == self:
                return
        else:
            if shape_name == self.get_name():
                return
            if not self.parent_shape:
                return
            locked_to_shape = self.parent_shape.get_interior_shape(shape_name)
        if self.locked_to_shape:
            self.locked_to_shape.init_locked_shapes()
            self.locked_to_shape.remove_interior_shape(
                    self, self.locked_to_shape.locked_shapes, lock=True)

        if locked_to_shape:
            locked_to_shape.init_locked_shapes()
            if direct:
                locked_to_shape.locked_shapes.add(self)
                self.locked_to_shape = locked_to_shape
            else:
                locked_to_shape.add_interior_shape(self, locked_to_shape.locked_shapes, lock=True)

    def get_locked_to(self):
        if self.locked_to_shape:
            return self.locked_to_shape.get_shape_path(self.parent_shape)
        return ""

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = ["anchor_at", "border_color", "border_width", "fill_color",
                      "width", "height", "scale_x", "scale_y",
                      "angle", "pre_matrix", "post_scale_x", "post_scale_y",
                      "x", "y", "visible"]
        return prop_names

    def get_pose_prop_dict(self):
        prop_dict = dict()
        for prop_name in self.get_pose_prop_names():
            value = self.get_prop_value(prop_name)
            if isinstance(value, cairo.Matrix):
                value = Matrix.copy(value) if value else None
            elif value and hasattr(value, "copy"):
                value = value.copy()
            elif type(value) not in (int, float, str, bool) and value is not None:
                raise Exception("Don't know how to copy {0} of type {1}".format(prop_name, type(value)))
            prop_dict[prop_name] = value
        return prop_dict

    def set_pose_prop_from_dict(self, prop_dict, non_direct_props=None):
        for prop_name in self.get_pose_prop_names():
            if prop_name in prop_dict:
                value = prop_dict[prop_name]
                if isinstance(value, cairo.Matrix):
                    value = Matrix.copy(value) if value else None
                if hasattr(self, prop_name) and \
                   (non_direct_props is None or prop_name not in non_direct_props):
                    #directly attach the prop value, no transformation is needed.
                    setattr(self, prop_name, copy_value(value))
                else:
                    self.set_prop_value(prop_name, value)

    @classmethod
    def get_pose_prop_xml_element(cls, shape_name, prop_dict):
        pose_shape_elm = XmlElement(cls.POSE_SHAPE_TAG_NAME)
        pose_shape_elm.attrib["name"] = shape_name
        for prop_name, value in prop_dict.items():
            if prop_name in ("form_raw",):
                pose_shape_elm.append(value.get_xml_element())
            else:
                if hasattr(value, "to_text"):
                    value = value.to_text()
                pose_shape_elm.attrib[prop_name] = "{0}".format(value)
        return pose_shape_elm

    @staticmethod
    def create_pose_prop_dict_from_xml_element(elm):
        shape_name = None
        prop_dict = dict()
        for prop_name, value in elm.attrib.items():
            if prop_name == "name":
                shape_name = value
                continue
            if prop_name in ("anchor_at", "translation", "abs_anchor_at", "rel_abs_anchor_at"):
                value = Point.from_text(value)
            elif prop_name in ("fill_color", "border_color"):
                value = color_from_text(value)
            elif prop_name == "pre_matrix":
                value = Matrix.from_text(value)
            elif prop_name in ("pose", "text", "font"):
                value = value
            elif prop_name == "visible":
                if value == "True":
                    value = True
                elif value == "False":
                    value = False
                else:
                    value = bool(int(value))
            else:
                try:
                    value = float(value)
                except ValueError:
                    continue
            prop_dict[prop_name] = value
        return (shape_name, prop_dict)

    def set_transition_pose_prop_from_dict(self, start_prop_dict, end_prop_dict, frac):
        for prop_name in self.get_pose_prop_names():
            if prop_name not in start_prop_dict or prop_name not in end_prop_dict: continue
            start_value = start_prop_dict[prop_name]
            end_value = end_prop_dict[prop_name]
            if prop_name == "form_raw":
                prop_data=dict(start_form_raw=start_value, end_form_raw=end_value)
                self.set_prop_value("internal", frac, prop_data)
            elif prop_name == "pose":
                prop_data=dict(start_pose=start_value, end_pose=end_value, type="pose")
                self.set_prop_value("internal", frac, prop_data)
            elif prop_name == "form_name":
                prop_data=dict(start_form=start_value, end_form=end_value)
                self.set_prop_value("internal", frac, prop_data)
            elif type(start_value) in (int, float):
                self.set_prop_value_direct(prop_name, start_value+(end_value-start_value)*frac)
            elif prop_name in ("visible",) or \
                        type(start_value) in (bool, ):
                value = int(start_value)+(int(end_value)-int(start_value))*frac
                value = bool(int(round(value)))
                self.set_prop_value_direct(prop_name, value)
            elif type(start_value) in (str, ):
                self.set_prop_value_direct(prop_name, start_value)
            elif isinstance(start_value, Point):
                self_point = Point(0,0)
                self_point.x = start_value.x + (end_value.x-start_value.x)*frac
                self_point.y = start_value.y + (end_value.y-start_value.y)*frac
                self.set_prop_value_direct(prop_name, self_point)
            elif isinstance(start_value, Color) or isinstance(start_value, GradientColor):
                self_color = self.get_prop_value(prop_name)
                if self_color:
                    self_color = self_color.copy()
                    self_color.set_inbetween(start_value, end_value, frac)
                    self.set_prop_value_direct(prop_name, self_color)
            elif isinstance(start_value, cairo.Matrix):
                if start_value and end_value:
                    current_value = Matrix.interpolate(start_value, end_value, frac)
                else:
                    current_value = None
                self.set_prop_value_direct(prop_name, current_value)

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["type"] = self.TYPE_NAME
        elm.attrib["name"] = self._name
        elm.attrib["moveable"] = ("1" if self.moveable else "0")
        if self.locked_to_shape:
            elm.attrib["locked_to"] = self.locked_to_shape.get_shape_path(root_shape=self.parent_shape)
        if not self.visible:
            elm.attrib["visible"] = "0"
        if not self.renderable:
            elm.attrib["renderable"] = "0"
        if self.same_xy_scale:
            elm.attrib["same_xy_scale"] = "1"
        elm.attrib["anchor_at"] = self.anchor_at.to_text()
        if self.border_color:
            elm.attrib["border_color"] = self.border_color.to_text()
        elm.attrib["border_width"] = "{0}".format(self.border_width)
        if self.fill_color:
            elm.attrib["fill_color"] = self.fill_color.to_text()
        elm.attrib["width"] = "{0}".format(self.width)
        elm.attrib["height"] = "{0}".format(self.height)
        elm.attrib["scale_x"] = "{0}".format(self.scale_x)
        elm.attrib["scale_y"] = "{0}".format(self.scale_y)
        elm.attrib["translation"] = self.translation.to_text()
        elm.attrib["angle"] = "{0}".format(self.angle)
        elm.attrib["post_scale_x"] = "{0}".format(self.post_scale_x)
        elm.attrib["post_scale_y"] = "{0}".format(self.post_scale_y)
        if self.border_dashes:
            elm.attrib["border_dash"] = self.get_border_dash()
        if self.pre_matrix:
            elm.attrib["pre_matrix"] = Matrix.to_text(self.pre_matrix)
        if isinstance(self, Mirror):
            Mirror.set_xml_element(self, elm)
        if not self.selectable:
            elm.attrib["sel"] = "0"
        return elm

    @classmethod
    def get_params_array_from_xml_element(cls, elm):
        anchor_at_str = elm.attrib.get("anchor_at", Point(0,0).to_text())
        border_color_str = elm.attrib.get("border_color", None)
        border_width = elm.attrib.get("border_width", 0)
        fill_color_str = elm.attrib.get("fill_color", None)
        width_str = elm.attrib.get("width", "1")
        height_str = elm.attrib.get("height", "1")
        arr = []
        arr.append(Point.from_text(anchor_at_str))
        arr.append(color_from_text(border_color_str))
        arr.append(float(border_width))
        arr.append(color_from_text(fill_color_str))
        arr.append(float(width_str))
        arr.append(float(height_str))
        return arr

    def assign_params_from_xml_element(self, elm, all_fields=False):
        self.moveable = bool(int(elm.attrib.get("moveable", 1)))
        self.visible = bool(int(elm.attrib.get("visible", 1)))
        self.renderable = bool(int(elm.attrib.get("renderable", 1)))
        self.same_xy_scale = bool(int(elm.attrib.get("same_xy_scale", False)))
        self.scale_x = float(elm.attrib.get("scale_x", 1))
        self.scale_y = float(elm.attrib.get("scale_y", 1))
        locked_to =  elm.attrib.get("locked_to")
        if locked_to:
            self._locked_to = locked_to

        translation_str = elm.attrib.get("translation", None)
        if translation_str:
            self.translation.copy_from(Point.from_text(translation_str))

        self.angle = float(elm.attrib.get("angle", 0))
        self.post_scale_x = float(elm.attrib.get("post_scale_x", 1))
        self.post_scale_y = float(elm.attrib.get("post_scale_y", 1))
        pre_matrix_str = elm.attrib.get("pre_matrix", None)
        if pre_matrix_str:
            self.pre_matrix = Matrix.from_text(pre_matrix_str)
        name = elm.attrib.get("name", None)
        if name:
            self._name = name.replace(".", "")
        if isinstance(self, Mirror):
            Mirror.assign_params_from_xml_element(self, elm)
        if all_fields:
            self.width = float(elm.attrib.get("width", 1))
            self.height = float(elm.attrib.get("height", 1))
            #TODO
            #rest of the fiels needs to be implemented, but later.
        self.set_border_dash(elm.attrib.get("border_dash", ""))
        self.selectable = bool(int(elm.attrib.get("sel", 1)))

    def copy_into(self, newob, copy_name=False, all_fields=False):
        newob.visible = self.visible
        newob.moveable = self.moveable
        newob.renderable = self.renderable
        if self.locked_to_shape:
            newob._locked_to = self.get_locked_to()
        newob.same_xy_scale = self.same_xy_scale
        newob.translation = self.translation.copy()
        newob.angle = self.angle
        newob.pre_matrix = Matrix.copy(self.pre_matrix) if self.pre_matrix else None
        newob.scale_x = self.scale_x
        newob.scale_y = self.scale_y
        newob.post_scale_x = self.post_scale_x
        newob.post_scale_y = self.post_scale_y
        newob.set_border_dash(self.get_border_dash())
        if copy_name:
            newob._name = self._name
        newob.parent_shape = self.parent_shape
        if all_fields:
            newob.anchor_at.copy_from(self.anchor_at)
            if self.border_color:
                if not newob.border_color:
                    newob.border_color = self.border_color.copy()
                else:
                    newob.border_color.copy_from(self.border_color)
            else:
                newob.border_color = None
            newob.border_width = self.border_width
            if self.fill_color:
                if not newob.fill_color:
                    newob.fill_color = self.fill_color.copy()
                else:
                    newob.fill_color.copy_from(self.fill_color)
            else:
                newob.fill_color = None
            newob.width = self.width
            newob.height = self.height
        if isinstance(self, Mirror) and isinstance(newob, Mirror):
            Mirror.copy_into(self, newob)

    def __hash__(self):
        return hash(self.id_num)

    def __eq__(self, other):
        return isinstance(other, Shape) and self.id_num == other.id_num

    def __ne__(self, other):
        return not (self == other)

    def get_name(self):
        return self._name

    def set_visible(self, value):
        if isinstance(value, str):
            self.visible = (value=="True")
        else:
            self.visible = bool(value)

    def can_draw_time_slice_for(self, prop_name):
        return False

    def set_prop_value(self, prop_name, value, prop_data=None):
        if prop_name == "followed_upto":
            self.set_followed_upto(value, prop_data)
        set_attr_name = "set_" + prop_name
        if hasattr(self, set_attr_name):
            getattr(self, set_attr_name)(value)
        elif hasattr(self, prop_name):
            setattr(self, prop_name, value)

    def set_prop_value_direct(self, prop_name, value):
        if hasattr(self, prop_name):
            setattr(self, prop_name, copy_value(value))
        else:
            self.set_prop_value(prop_name, value)

    def get_prop_value(self, prop_name):
        get_attr_name = "get_" + prop_name
        if hasattr(self, get_attr_name):
            return getattr(self, get_attr_name)()
        elif hasattr(self, prop_name):
            return getattr(self, prop_name)
        return None

    def get_prop_value_for_time_slice(self, prop_name):
        prop_value = self.get_prop_value(prop_name)
        if hasattr(prop_value, "to_array"):
            return prop_value.to_array()
        return prop_value

    def has_prop(self, prop_name):
        get_attr_name = "get_" + prop_name
        if hasattr(self, get_attr_name):
            return True
        elif hasattr(self, prop_name):
            return True
        return False

    def get_angle(self):
        return self.angle

    def set_border_width(self, border_width):
        self.border_width = border_width

    def get_border_width(self):
        return self.border_width

    def get_border_dash(self):
        if not self.border_dashes:
            return ""
        text = ",".join("{0}".format(v) for v in self.border_dashes)
        if self.border_dash_offset:
            text += ":{0}".format(self.border_dash_offset)
        return text

    def set_border_dash(self, value):
        arr1 = value.split(":")
        if len(arr1)>1:
            try:
                self.border_dash_offset = float(arr1[1])
            except:
                pass
        arr2 = arr1[0].split(",")
        dashes = []
        for i in range(len(arr2)):
            try:
                dashes.append(float(arr2[i]))
            except:
                pass
        self.border_dashes = dashes

    def set_border_color(self, color):
        if color is None:
            self.border_color = None
        elif isinstance(self.border_color, Color) and isinstance(color, Color):
            self.border_color.copy_from(color)
        else:
            self.border_color = color

    def get_border_color(self):
        return self.border_color

    def set_fill_color(self, color):
        if color is None:
            self.fill_color = None
        elif isinstance(self.fill_color, Color) and isinstance(color, Color):
            self.fill_color.copy_from(color)
        else:
            self.fill_color = color

    def get_fill_color(self):
        return self.fill_color

    def get_width(self): return self.width

    def set_width(self, value, fixed_anchor=True):
        if value == 0:
            value = .00001
        if value >0:
            if fixed_anchor:
                abs_anchor_at = self.get_abs_anchor_at()
                self.anchor_at.x *= float(value)/self.width
            self.width = value
            if fixed_anchor:
                self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def get_height(self): return self.height

    def set_height(self, value, fixed_anchor=True):
        if value == 0:
            value = .00001
        if value>0:
            if fixed_anchor:
                abs_anchor_at = self.get_abs_anchor_at()
                self.anchor_at.y *= float(value)/self.height
            self.height = value
            if fixed_anchor:
                self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def get_anchor_x(self):
        return self.anchor_at.x

    def set_anchor_x(self, value):
        self.anchor_at.x = value

    def get_anchor_y(self):
        return self.anchor_at.y

    def set_anchor_y(self, value):
        self.anchor_at.y = value

    def set_anchor_at(self, x, y=None):
        if isinstance(x, Point):
            self.anchor_at.copy_from(x)
            return
        self.anchor_at.x = x
        self.anchor_at.y = y

    def move_x_to(self, x):
        self.move_to(x, self.get_abs_anchor_at().y)

    def move_y_to(self, y):
        self.move_to(self.get_abs_anchor_at().x, y)

    def set_x(self, x):
        xy = self.get_xy()
        xy.x = x
        self.set_xy(xy)

    def set_y(self, y):
        xy = self.get_xy()
        xy.y = y
        self.set_xy(xy)

    def get_x(self):
        return float(self.get_xy().x)

    def get_y(self):
        return float(self.get_xy().y)

    def get_xy(self):
        xy = self.get_abs_anchor_at()
        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if parent_shape:
            xy.x -= parent_shape.anchor_at.x
            xy.y -= parent_shape.anchor_at.y
        return xy

    def set_xy(self, xy):
        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if isinstance(xy, list):
            if parent_shape:
                self.move_to(xy[0]+parent_shape.anchor_at.x, xy[1]+parent_shape.anchor_at.y)
            else:
                self.move_to(xy[0], xy[1])
        else:
            if parent_shape:
                self.move_to(xy.x+parent_shape.anchor_at.x, xy.y+parent_shape.anchor_at.y)
            else:
                self.move_to(xy.x, xy.y)

    def get_stage_xy(self):
        xy = self.get_abs_anchor_at()
        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if parent_shape:
            parent_anchor = parent_shape.anchor_at
            xy.translate(-parent_anchor.x, -parent_anchor.y)
        return xy

    def get_stage_x(self):
        return self.get_stage_xy().x

    def get_stage_y(self):
        return self.get_stage_xy().y

    def set_stage_xy(self, point):
        if not point: return
        xy = point.copy()
        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if parent_shape:
            parent_anchor = parent_shape.anchor_at
            xy.translate(parent_anchor.x, parent_anchor.y)
        self.move_to(xy.x, xy.y)

    def set_stage_x(self, x):
        xy = Point(x, self.get_abs_anchor_at().y)
        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if parent_shape:
            xy.x += parent_shape.anchor_at.x
        self.move_to(xy.x, xy.y)

    def set_stage_y(self, y):
        xy = Point( self.get_abs_anchor_at().x, y)
        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if parent_shape:
            xy.y += parent_shape.anchor_at.y
        self.move_to(xy.x, xy.y)

    def set_scale_x(self, sx):
        if sx == 0:
            sx = .00001
        abs_anchor_at = self.get_abs_anchor_at()
        self.scale_x = sx
        if self.same_xy_scale:
            self.scale_y = sx
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def set_scale_y(self, sy):
        if sy == 0:
            sy = .00001
        abs_anchor_at = self.get_abs_anchor_at()
        self.scale_y = sy
        if self.same_xy_scale:
            self.scale_x = sy
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def set_same_xy_scale(self, value):
        if value and not self.same_xy_scale:
            self.set_scale_x((self.scale_x+self.scale_y)*.5)
        self.same_xy_scale = bool(value)

    def translate(self, dx, dy):
        self.translation.x += dx
        self.translation.y += dy

    def prepend_pre_matrix(self, matrix):
        if not self.pre_matrix:
            self.pre_matrix = cairo.Matrix()
        self.pre_matrix = self.pre_matrix*matrix

    def set_angle(self, angle):
        rel_left_top_corner = Point(-self.anchor_at.x, -self.anchor_at.y)
        rel_left_top_corner.scale(self.post_scale_x, self.post_scale_y)
        rel_left_top_corner.rotate_coordinate(-angle)
        rel_left_top_corner.scale(self.scale_x, self.scale_y)
        if self.pre_matrix:
            rel_left_top_corner.transform(self.pre_matrix)
        abs_anchor = self.get_abs_anchor_at()
        rel_left_top_corner.translate(abs_anchor.x, abs_anchor.y)
        self.angle = angle
        self.translation.x = rel_left_top_corner.x
        self.translation.y = rel_left_top_corner.y

    def get_abs_anchor_at(self):
        abs_anchor = self.anchor_at.copy()
        abs_anchor.scale(self.post_scale_x, self.post_scale_y)
        abs_anchor.rotate_coordinate(-self.angle)
        abs_anchor.scale(self.scale_x, self.scale_y)
        if self.pre_matrix:
            abs_anchor.transform(self.pre_matrix)
        abs_anchor.translate(self.translation.x, self.translation.y)
        return abs_anchor

    def set_abs_anchor_at(self, point):
        self.move_to(point.x, point.y)

    def shift_abs_anchor_at(self, shift):
        abs_anchor_at = self.get_abs_anchor_at()
        abs_anchor_at.translate(shift.x, shift.y)
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def move_to(self, x, y):
        point = Point(x,y)
        abs_anchor_at = self.get_abs_anchor_at()
        point.translate(-abs_anchor_at.x, -abs_anchor_at.y)
        self.translation.x += point.x
        self.translation.y += point.y

    def transform_point(self, point):
        point = Point(point.x, point.y)
        abs_anchor_at = self.get_abs_anchor_at()
        point.translate(-abs_anchor_at.x, -abs_anchor_at.y)
        if self.pre_matrix:
            point.reverse_transform(self.pre_matrix)
        point.scale(1./self.scale_x, 1./self.scale_y)
        point.rotate_coordinate(self.angle)
        point.scale(1./self.post_scale_x, 1./self.post_scale_y)
        point.translate(self.anchor_at.x, self.anchor_at.y)
        return point

    def get_active_parent_shape(self):
        if self.locked_to_shape:
            return self.locked_to_shape
        return self.parent_shape

    def transform_locked_shape_point(self, point, root_shape=None,
                                           exclude_last=True, include_root=False):
        if root_shape is None:
            root_shape = self.parent_shape
        ancestors = self.get_shape_ancestors(root_shape=root_shape, lock=True, include_root=True)
        if ancestors and root_shape and root_shape != ancestors[0]:
            rel_root_shape = root_shape
            while rel_root_shape:
                if rel_root_shape in ancestors:
                    root_shape_index = ancestors.index(rel_root_shape)
                    ancestors = ancestors[root_shape_index:]
                    break
                point = rel_root_shape.reverse_transform_point(point)
                if rel_root_shape.locked_to_shape:
                    rel_root_shape = rel_root_shape.locked_to_shape
                else:
                    rel_root_shape = rel_root_shape.parent_shape
        if exclude_last:
            ancestors = ancestors[:-1]
        if not include_root:
            ancestors = ancestors[1:]
        for shape in ancestors:
            point = shape.transform_point(point)
        return point

    def reverse_transform_locked_shape_point(self, point, root_shape=None):
        if root_shape is None:
            root_shape = self.parent_shape
        ancestors = self.get_shape_ancestors(root_shape=root_shape, lock=True, include_root=True)
        transformers = []
        if ancestors and root_shape and root_shape != ancestors[0]:
            rel_root_shape = root_shape
            while rel_root_shape:
                if rel_root_shape in ancestors:
                    root_shape_index = ancestors.index(rel_root_shape)
                    ancestors = ancestors[root_shape_index:]
                    break
                transformers.insert(0, rel_root_shape)
                if rel_root_shape.locked_to_shape:
                    rel_root_shape = rel_root_shape.locked_to_shape
                else:
                    rel_root_shape = rel_root_shape.parent_shape
        if len(ancestors) == 1 and root_shape is None:
            point = self.reverse_transform_point(point)
        else:
            for shape in reversed(ancestors[1:]):
                point = shape.reverse_transform_point(point)
        for shape in transformers:
            point = shape.transform_point(point)
        return point

    def abs_transform_distance(self, d):
        origin = self.transform_locked_shape_point(
                Point(0,0), root_shape=0, exclude_last=False, include_root=True)
        corner = self.transform_locked_shape_point(
                Point(abs(d), 0), root_shape=0, exclude_last=False, include_root=True)
        return corner.distance(origin)

    def reverse_transform_point(self, point):
        point = Point(point.x, point.y)
        point.translate(-self.anchor_at.x, -self.anchor_at.y)
        point.scale(self.post_scale_x, self.post_scale_y)
        point.rotate_coordinate(-self.angle)
        point.scale(self.scale_x, self.scale_y)
        if self.pre_matrix:
            point.transform(self.pre_matrix)
        abs_anchor = self.get_abs_anchor_at()
        point.translate(abs_anchor.x, abs_anchor.y)
        return point

    def abs_reverse_transform_point(self, point, root_shape=None):
        point = self.reverse_transform_point(point)
        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if parent_shape and parent_shape != root_shape:
            point = parent_shape.abs_reverse_transform_point(point, root_shape=root_shape)
        return point

    def abs_angle(self, angle):
        points = [Point(0,0), Point(1, 0)]
        points[1].rotate_coordinate(angle)
        shape = self
        while shape:
            points[0] = shape.reverse_transform_point(points[0])
            points[1] = shape.reverse_transform_point(points[1])
            if shape.locked_to_shape:
                shape = shape.locked_to_shape
            else:
                shape = shape.parent_shape
        point = points[1].diff(points[0])
        return math.atan2(point.y, point.x)/RAD_PER_DEG

    def pre_draw(self, ctx, root_shape=None):
        if self == root_shape:
            return

        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if parent_shape:
            parent_shape.pre_draw(ctx, root_shape=root_shape)
        ctx.translate(self.translation.x, self.translation.y)
        if self.pre_matrix:
            ctx.set_matrix(self.pre_matrix*ctx.get_matrix())
        ctx.scale(self.scale_x, self.scale_y)
        ctx.rotate(self.angle*RAD_PER_DEG)
        ctx.scale(self.post_scale_x, self.post_scale_y)

    def reverse_pre_draw(self, ctx, root_shape=None):
        ctx.scale(1./self.post_scale_x, 1./self.post_scale_y)
        ctx.rotate(-self.angle*RAD_PER_DEG)
        ctx.scale(1./self.scale_x, 1./self.scale_y)
        if self.pre_matrix:
            ctx.set_matrix(ctx.get_matrix()*self.pre_matrix)
        ctx.translate(-self.translation.x, -self.translation.y)

        if self.locked_to_shape:
            parent_shape = self.locked_to_shape
        else:
            parent_shape = self.parent_shape

        if parent_shape and parent_shape != root_shape:
            parent_shape.reverse_pre_draw(ctx, root_shape=root_shape)

    def draw_anchor(self, ctx):
        ctx.translate(self.anchor_at.x, self.anchor_at.y)
        ctx.arc(0, 0, 5, 0, math.pi*2)
        ctx.arc(0, 0, 2, 0, math.pi*2)

    def draw_border(self, ctx):
        if self.border_color is None: return
        if self.border_dashes:
            ctx.set_dash(self.border_dashes, self.border_dash_offset)
        else:
            ctx.set_dash([])
        draw_stroke(ctx, self.border_width, self.border_color)

    def draw_fill(self, ctx):
        if self.fill_color is None: return
        draw_fill(ctx, self.fill_color)

    def fill_shape_area(self, ctx, root_shape=None):
        if self.fill_color is not None:
            ctx.save()
            self.pre_draw(ctx, root_shape=root_shape)
            self.draw_path(ctx, for_fill=True)
            self.draw_fill(ctx)
            ctx.restore()

    def storke_shape_area(self, ctx, root_shape=None, fixed_border=True):
        if self.border_color is not None:
            ctx.save()
            self.pre_draw(ctx, root_shape=root_shape)
            self.draw_path(ctx, for_fill=False)
            if fixed_border:
                ctx.restore()
                self.draw_border(ctx)
            else:
                self.draw_border(ctx)
                ctx.restore()

    def draw(self, ctx, fixed_border=True, root_shape=None):
        if self.fill_color is not None:
            ctx.save()
            self.pre_draw(ctx, root_shape=root_shape)
            self.draw_path(ctx, for_fill=True)
            self.draw_fill(ctx)
            ctx.restore()

        if self.border_color is not None:
            ctx.save()
            self.pre_draw(ctx, root_shape=root_shape)
            self.draw_path(ctx, for_fill=False)
            if fixed_border:
                ctx.restore()
                self.draw_border(ctx)
            else:
                self.draw_border(ctx)
                ctx.restore()

    def draw_axis(self, ctx):
        ctx.save()
        self.pre_draw(ctx)

        ctx.save()
        ctx.translate(self.anchor_at.x, self.anchor_at.y)
        ctx.set_line_width(3)

        for angle, color in [[0, "ff0000"], [90, "00ff00"]]:
            ctx.rotate(angle*RAD_PER_DEG)
            ctx.set_source_rgba(*Color.parse(color).get_array())
            ctx.move_to(0, 0)
            ctx.line_to(95, 0)
            ctx.stroke()

            ctx.move_to(100, 0)
            ctx.line_to(100-10, -5)
            ctx.line_to(100-10, 5)
            ctx.line_to(100, 0)
            ctx.fill()
        ctx.restore()

        self.draw_anchor(ctx)
        ctx.restore()
        self.draw_border(ctx)

    def get_outline(self, padding):
        return Rect(-padding, -padding, self.width+2*padding, self.height+2*padding, padding)

    def get_abs_outline(self, padding=0, root_shape=None):
        outline = self.get_outline(padding)
        points = []
        points.append(Point(outline.left, outline.top))
        points.append(Point(outline.left + outline.width, outline.top))
        points.append(Point(outline.left + outline.width, outline.top + outline.height))
        points.append(Point(outline.left, outline.top + outline.height))

        #abs_anchor_at = self.get_abs_anchor_at()
        min_x = max_x = min_y = max_y =  None
        if root_shape is None:
            root_shape = self.get_active_parent_shape()
        for point in points:
            point = self.reverse_transform_locked_shape_point(point, root_shape=root_shape)
            #point = self.reverse_transform_point(point)

            if min_x is None or min_x>point.x: min_x = point.x
            if max_x is None or max_x<point.x: max_x = point.x
            if min_y is None or min_y>point.y: min_y = point.y
            if max_y is None or max_y<point.y: max_y = point.y

        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def get_abs_reverse_outline(self, left, top, width, height, root_shape=None):
        points = []
        points.append(Point(left, top))
        points.append(Point(left + width, top))
        points.append(Point(left + width, top + height))
        points.append(Point(left, top + height))

        min_x = max_x = min_y = max_y =  None
        for point in points:
            point = self.abs_reverse_transform_point(point, root_shape=root_shape)

            if min_x is None or min_x>point.x: min_x = point.x
            if max_x is None or max_x<point.x: max_x = point.x
            if min_y is None or min_y>point.y: min_y = point.y
            if max_y is None or max_y<point.y: max_y = point.y

        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def is_within(self, point, margin=0):
        point = self.transform_point(point)
        return point.x>=-margin and point.x<=self.width+margin and \
               point.y>=-margin and point.y<=self.height+margin

    def is_inside_rect(self, rect):
        abso = self.get_abs_outline(0)
        points = []
        points.append(Point(abso.left, abso.top))
        points.append(Point(abso.left+abso.width, abso.top))
        points.append(Point(abso.left+abso.width, abso.top+abso.height))
        points.append(Point(abso.left, abso.top+abso.height))
        for point in points:
            if not (rect.left<=point.x and point.x<=rect.left+rect.width and \
                    rect.top<=point.y and point.y<=rect.top+rect.height):
                return False
        return True

    def flip(self, direction):
        pass

    def recreate_name(self):
        self._name = self.new_name()

    def rename(self, name):
        self._name = name

    def place_anchor_at_center(self):
        self.anchor_at.x = self.get_width()*.5
        self.anchor_at.y = self.get_height()*.5

    def get_surface(self, width, height, padding=5):
        pixbuf = Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, width, height)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(), pixbuf.get_height())
        ctx = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, 0, 0)
        ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

        eff_width = width-2*padding
        eff_height = height-2*padding
        scale = min(eff_width*1./self.width, eff_height*1./self.height)
        ctx.translate((width-scale*self.width)*.5, (height-scale*self.height)*.5)
        ctx.scale(scale, scale)
        #ctx.translate(-self.translation.x, -self.translation.y)
        set_default_line_style(ctx)
        self.draw(ctx, Point(self.width, self.height), root_shape=self)
        return ctx.get_target()

    def get_pixbuf(self, width, height=None):
        if height is None:
            height = width
        surface= self.get_surface(width, height)
        pixbuf= Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())
        return pixbuf

    def get_anchor_shape(self):
        if not hasattr(self, "anchor_shape"):
            self.anchor_shape = AnchorShape(parent_shape=self)
        return self.anchor_shape

    NAME_SEED = 0
    _APP_EPOCH_TIME = time.mktime(time.strptime("1 Jan 2016", "%d %b %Y"))

    @staticmethod
    def new_name():
        Shape.NAME_SEED += 1
        elapsed_time = round(time.time()-Shape._APP_EPOCH_TIME, 3)
        return "{0}_{1}".format(elapsed_time, Shape.NAME_SEED).replace(".", "")

    @staticmethod
    def rounded_rectangle(ctx, x, y, w, h, r=20):
        # This is just one of the samples from
        # http://www.cairographics.org/cookbook/roundedrectangles/
        #   A****BQ
        #  H      C
        #  *      *
        #  G      D
        #   F****E
        if r == 0:
            ctx.rectangle(x, y, w, h)
        else:
            ctx.move_to(x+r,y)                      # Move to A
            ctx.line_to(x+w-r,y)                    # Straight line to B
            ctx.curve_to(x+w,y,x+w,y,x+w,y+r)       # Curve to C, Control points are both at Q
            ctx.line_to(x+w,y+h-r)                  # Move to D
            ctx.curve_to(x+w,y+h,x+w,y+h,x+w-r,y+h) # Curve to E
            ctx.line_to(x+r,y+h)                    # Line to F
            ctx.curve_to(x,y+h,x,y+h,x,y+h-r)       # Curve to G
            ctx.line_to(x,y+r)                      # Line to H
            ctx.curve_to(x,y,x,y,x+r,y)             # Curve to A

    @staticmethod
    def quadrilateral(ctx, left_top, right_top, right_bottom, left_bottom):
        ctx.new_path()
        ctx.move_to(left_top.x, left_top.y)
        ctx.line_to(right_top.x, right_top.y)
        ctx.line_to(right_bottom.x, right_bottom.y)
        ctx.line_to(left_bottom.x, left_bottom.y)
        ctx.line_to(left_top.x, left_top.y)
        ctx.close_path()

    @staticmethod
    def draw_selection_border(ctx):
        ctx.save()
        ctx.set_source_rgb(0,0,0)
        ctx.set_line_width(1)
        ctx.set_dash([5])
        ctx.stroke()
        ctx.restore()

    @staticmethod
    def stroke(ctx, line_width, color=Color(0,0,0,1), dash=[]):
        ctx.save()
        ctx.set_source_rgba(*color.get_array())
        ctx.set_line_width(line_width)
        ctx.set_dash(dash)
        ctx.stroke()
        ctx.restore()

ANCHOR_SHAPE_NAME = "_anchor_"

class AnchorShape(Shape):
    def __init__(self, parent_shape):
        super(AnchorShape, self).__init__(Point(0,0), None, 0., None, 0., 0.)
        del self.translation
        self.parent_shape = parent_shape
        self._name = ANCHOR_SHAPE_NAME

    def __getattr__(self, name):
        if name == "translation":
            return self.parent_shape.anchor_at
        else:
            raise AttributeError

