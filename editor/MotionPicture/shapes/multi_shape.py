from ..commons import *
from .shape import Shape
from .shape_list import ShapeList
from .rectangle_shape import RectangleShape
from .oval_shape import OvalShape
from .ring_shape import RingShape
from .curve_shape import CurveShape
from .polygon_shape import PolygonShape
from .image_shape import ImageShape
from .image_seq_shape import ImageSeqShape
from .video_shape import VideoShape
from .audio_shape import AudioShape
from .text_shape import TextShape
from .camera_shape import CameraShape
from .threed_shape import ThreeDShape
from .document_shape import DocumentShape
from .custom_shape import CustomShape
from .curve_joiner_shape import CurveJoinerShape
from .mimic_shape import MimicShape
from .curves_form import CurvesForm
from xml.etree.ElementTree import Element as XmlElement
from .custom_props import *
from .mimic_shape import MimicShape

REL_ABS_ANCHOR_AT = "rel_abs_anchor_at"

class MultiShapeModule(object):
    Modules = dict()

    def __init__(self, module_name, module_path):
        self.module_name = module_name
        self.module_path = module_path
        self.root_multi_shape = None
        MultiShapeModule.Modules[self.module_name] = self

    @classmethod
    def create(cls, module_name, module_path):
        if module_name in MultiShapeModule.Modules:
            return None
        return cls(module_name, module_path)

    def load(self):
        pass

    def unload(self):
        pass

    @staticmethod
    def get_multi_shape(path):
        names = path.split(".")
        module = MultiShapeModule.Modules.get(names[0])
        if module:
            module.load()
            multi_shape = module.root_multi_shape
            for i in range(1, len(names)):
                name = names[i]
                shape = multi_shape.shapes.get_item_by_name(name)
                if shape is None or not isinstance(shape, MultiShape):
                    module.unload()
                    return None
                multi_shape = shape
            multi_shape = multi_shape.copy(deep_copy=True)
            multi_shape.perform_post_create_from_xml()
            multi_shape.imported_from = path
            multi_shape.imported_anchor_at = multi_shape.anchor_at.copy()
            module.unload()
            return multi_shape
        return None

class MultiShape(Shape):
    TYPE_NAME = "multi_shape"
    POSE_TAG_NAME = "pose"

    def __init__(self, anchor_at=None, border_color=None,
                       border_width=0, fill_color=None, width=1, height=1):
        if anchor_at is None:
            anchor_at = Point(width*.5, height*.5)
        Shape.__init__(self,  anchor_at, border_color, border_width, fill_color, width, height)
        self.shapes = ShapeList()
        self.poses = dict()
        self.timelines = dict()
        self.masked = False
        self.custom_props = None
        self.camera = None
        self.pose = None
        self.imported_from = None
        self.imported_anchor_at = None#this prop might get deleted in future.
        self.pose_pixbufs = dict()
        self.custom_props_editable = True

    def get_pose_pixbuf(self, pose_name):
        if pose_name not in self.pose_pixbufs:
            multi_shape = self.copy(
                    deep_copy=True, copy_name=True, copy_pixbufs=False,
                    copy_poses=False, copy_timelines=False)
            multi_shape.set_pose_raw(self.get_pose_by_name(pose_name))
            multi_shape.perform_post_create_from_xml()
            multi_shape.reset_transformations()
            multi_shape.parent_shape = None
            pixbuf = multi_shape.get_pixbuf(64, 64)
            self.pose_pixbufs[pose_name] = pixbuf
        return self.pose_pixbufs[pose_name]

    def delete_pose_pixbuf(self, pose_name):
        if pose_name in self.pose_pixbufs:
            del self.pose_pixbufs[pose_name]

    def get_interior_shapes(self):
        return self.shapes

    def has_poses(self):
        return True

    def get_shape_tree_list(self, prefix=""):
        items = []
        if not prefix:
            items.append(None)
        for shape in self.shapes:
            item_path = prefix+shape.get_name()
            items.append(item_path)
            if isinstance(shape, MultiShape):
                items.extend(shape.get_shape_tree_list(item_path+"."))
        return items

    def copy_data_from_linked(self, build_lock=True):
        if not self.linked_to: return

        interior_lock_list = self.get_interior_locked_shape_list(self.shapes.items)
        for shape, locked_to in interior_lock_list:
            shape.set_locked_to(None)

        for orig_shape in  self.linked_to.shapes:
            new_shape = orig_shape.copy(copy_name=True, deep_copy=True)
            new_shape.parent_shape = self
            self.shapes.replace_or_add(orig_shape.get_name(), new_shape)

        removable_shapes = []
        for child_shape in self.shapes:
            if not self.linked_to.shapes.contain(child_shape.get_name()):
                removable_shapes.append(child_shape)

        for removable_shape in removable_shapes:
            self.shapes.remove(removable_shape)
        del removable_shapes[:]

        self.shapes.order_like(self.linked_to.shapes.names)

        for shape, locked_to in interior_lock_list:
            shape.set_locked_to(locked_to)

        if build_lock:
            self.build_interior_locked_to(up=-10000000)

        if self.linked_to.custom_props:
            self.custom_props = self.linked_to.custom_props.copy(self)
        self.readjust_sizes()
        self.poses = copy_dict(self.linked_to.poses)
        self.timelines.clear()
        for key, timeline in self.linked_to.timelines.items():
            self.timelines[key] = timeline.copy(multi_shape=self)
        self.pose_pixbufs.clear()

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        if self.masked:
            elm.attrib["masked"] = "True"

        if not self.imported_from:
            for shape in self.shapes:
                elm.append(shape.get_xml_element())

            for pose_name, pose in self.poses.items():
                pose_elm = XmlElement(self.POSE_TAG_NAME)
                pose_elm.attrib["name"] = pose_name
                for shape_name, prop_dict in pose.items():
                    pose_shape_elm = self.get_pose_prop_xml_element(shape_name, prop_dict)
                    pose_elm.append(pose_shape_elm)
                elm.append(pose_elm)

            for timeline in self.timelines.values():
                elm.append(timeline.get_xml_element())
            if self.custom_props:
                elm.append(self.custom_props.get_xml_element())
        else:
            elm.attrib["imported_from"] = self.imported_from

        return elm

    @classmethod
    def create_from_xml_element(cls, elm, time_line_class):
        arr = Shape.get_params_array_from_xml_element(elm)
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        shape.masked = (elm.attrib.get("masked", None) == "True")
        for shape_element in elm.findall(Shape.TAG_NAME):
            shape_type = shape_element.attrib.get("type", None)
            child_shape = None
            if shape_type == RectangleShape.TYPE_NAME:
                child_shape = RectangleShape.create_from_xml_element(shape_element)
            elif shape_type == RingShape.TYPE_NAME:
                child_shape = RingShape.create_from_xml_element(shape_element)
            elif shape_type == OvalShape.TYPE_NAME:
                child_shape = OvalShape.create_from_xml_element(shape_element)
            elif shape_type == TextShape.TYPE_NAME:
                child_shape = TextShape.create_from_xml_element(shape_element)
            elif shape_type == ImageShape.TYPE_NAME:
                child_shape = ImageShape.create_from_xml_element(shape_element)
            elif shape_type == CurveShape.TYPE_NAME:
                child_shape = CurveShape.create_from_xml_element(shape_element)
            elif shape_type == PolygonShape.TYPE_NAME:
                child_shape = PolygonShape.create_from_xml_element(shape_element)
            elif shape_type == AudioShape.TYPE_NAME:
                child_shape = AudioShape.create_from_xml_element(shape_element)
            elif shape_type == VideoShape.TYPE_NAME:
                child_shape = VideoShape.create_from_xml_element(shape_element)
            elif shape_type == CameraShape.TYPE_NAME:
                child_shape = CameraShape.create_from_xml_element(shape_element)
            elif shape_type == MultiShape.TYPE_NAME:
                child_shape = MultiShape.create_from_xml_element(shape_element, time_line_class)
            elif shape_type == ThreeDShape.TYPE_NAME:
                child_shape = ThreeDShape.create_from_xml_element(shape_element)
            elif shape_type == DocumentShape.TYPE_NAME:
                child_shape = DocumentShape.create_from_xml_element(shape_element)
            elif shape_type == CustomShape.TYPE_NAME:
                child_shape = CustomShape.create_from_xml_element(shape_element)
            elif shape_type == CurveJoinerShape.TYPE_NAME:
                child_shape = CurveJoinerShape.create_from_xml_element(shape_element)
            elif shape_type == MimicShape.TYPE_NAME:
                child_shape = MimicShape.create_from_xml_element(shape_element)
            elif shape_type == ImageSeqShape.TYPE_NAME:
                child_shape = ImageSeqShape.create_from_xml_element(shape_element)
            if child_shape is None: continue
            child_shape.parent_shape = shape
            shape.shapes.add(child_shape)

        custom_prop_elm = elm.find(CustomProps.TAG_NAME)
        if custom_prop_elm:
            shape.custom_props = CustomProps.create_from_xml(custom_prop_elm, shape)

        for pose_elm in elm.findall(cls.POSE_TAG_NAME):
            pose_name = pose_elm.attrib["name"]
            pose = dict()
            for pose_shape_elm in pose_elm.findall(cls.POSE_SHAPE_TAG_NAME):
                shape_name, prop_dict = cls.create_pose_prop_dict_from_xml_element(pose_shape_elm)
                form = pose_shape_elm.find(CurvesForm.TAG_NAME)
                pose_shape = shape.get_interior_shape(shape_name)
                if not pose_shape:
                    continue
                if form:
                    if isinstance(pose_shape,CurveShape):
                        form_raw = CurvesForm.create_from_xml_element(form)
                    elif isinstance(pose_shape, PolygonShape):
                        form_raw = PolygonsForm.create_from_xml_element(form)
                    else:
                        form_raw = None
                    prop_dict["form_raw"] = form_raw
                if shape_name:
                    pose[shape_name] = prop_dict
            shape.poses[pose_name] = pose

        for time_line_elm in elm.findall(time_line_class.TAG_NAME):
            time_line = time_line_class.create_from_xml_element(time_line_elm, shape)
            shape.timelines[time_line.name] = time_line
        shape.imported_from = elm.attrib.get("imported_from", None)
        shape.sync_with_imported()

        return shape

    def build_locked_to(self, up=0):
        super(MultiShape, self).build_locked_to(up)
        self.build_interior_locked_to(up+1)

    def build_interior_locked_to(self, up=0):
        for child_shape in self.shapes:
            child_shape.build_locked_to(up)

    def perform_post_create_from_xml(self):
        for shape in self.shapes:
            if isinstance(shape, CurveJoinerShape):
                shape.build_joiner_items()
            elif isinstance(shape, MimicShape):
                shape.build_mimic_like_shape()
            elif isinstance(shape, MultiShape):
                shape.perform_post_create_from_xml()

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = super(MultiShape, cls).get_pose_prop_names()
        prop_names.append("pose")
        return prop_names

    def copy(self, copy_name=False, copy_shapes=True,
                                    deep_copy=False, copy_pixbufs=True,
                                    copy_poses=True, copy_timelines=True):
        newob = MultiShape(
            anchor_at=self.anchor_at.copy(), width=self.width, height=self.height)
        Shape.copy_into(self, newob, copy_name=copy_name, all_fields=deep_copy)
        if copy_shapes or deep_copy:
            for shape in self.shapes:
                child_shape = shape.copy(copy_name=True, deep_copy=deep_copy)
                child_shape.parent_shape = newob
                newob.shapes.add(child_shape)
            newob.build_interior_locked_to()
        if deep_copy:
            if copy_poses:
                newob.poses = copy_dict(self.poses)
            if copy_timelines:
                for key, timeline in self.timelines.items():
                    newob.timelines[key] = timeline.copy(newob)
        newob.masked = self.masked
        if self.custom_props:
            newob.custom_props = self.custom_props.copy(newob)

        newob.imported_from = self.imported_from
        newob.imported_anchor_at = copy_value(self.imported_anchor_at)
        return newob

    def sync_with_imported(self):
        if not self.imported_from:
            return

        multi_shape = MultiShapeModule.get_multi_shape(self.imported_from)
        if not multi_shape:
            return

        xy = self.get_xy()
        self.imported_anchor_at = multi_shape.anchor_at.copy()
        self.shapes.clear(destroy_items=True)
        for shape in multi_shape.shapes:
            shape.parent_shape = self
            self.shapes.add(shape)
        self.readjust_sizes()

        self.poses = multi_shape.poses
        self.custom_props = multi_shape.custom_props
        self.timelines.clear()
        for timeline_name, timeline in multi_shape.timelines.items():
            self.timelines[timeline_name] = timeline.copy(self)
        self.anchor_at.copy_from(multi_shape.anchor_at)
        self.set_xy(xy)

    def set_imported_from(self, name):
        self.imported_from = name
        self.sync_with_imported()

    def get_is_designable(self):
        return not bool(self.imported_from)

    def readjust_after_design_edit(self):
        return
        if self.imported_anchor_at:
            self.anchor_at.copy_from(self.imported_anchor_at)

    def save_pose(self, pose_name):
        if not pose_name:
            i = len(self.poses)
            while(True):
                i += 1
                pose_name = "Pose_{0:03}".format(i)
                if pose_name not in self.poses:
                    break

        self.poses[pose_name] = self.get_pose_raw()
        self.delete_pose_pixbuf(pose_name)
        return pose_name

    def get_pose_by_name(self, pose):
        if pose in self.poses:
            return self.poses[pose]
        return None

    def get_pose_raw(self):
        pose = dict()
        anchor_at = self.anchor_at
        for shape in self.shapes:
            prop_dict = shape.get_pose_prop_dict()
            pose[shape.get_name()] = prop_dict
            #rel_abs_anchor_at = shape.get_abs_anchor_at()
            #rel_abs_anchor_at.translate(-anchor_at.x, -anchor_at.y)
            #if not shape.locked_to_shape:
            #    prop_dict[REL_ABS_ANCHOR_AT] = rel_abs_anchor_at
        return pose

    def rename_pose(self, old_pose_name, new_pose_name):
        if new_pose_name in self.poses: return False
        pose = self.poses[old_pose_name]
        self.poses[new_pose_name] = pose
        del self.poses[old_pose_name]
        return True

    def delete_pose(self, pose_name):
        del self.poses[pose_name]
        self.delete_pose_pixbuf(pose_name)

    def set_pose(self, pose_name):
        if isinstance(pose_name, str):
            pose_name = pose_name.decode("utf-8")
        if pose_name not in self.poses: return
        self.pose = pose_name
        self.set_pose_raw(self.poses[pose_name])

    def set_pose_raw(self, pose):
        anchor_at = self.anchor_at.copy()
        for shape_name, prop_dict in pose.items():
            shape = self.shapes.get_item_by_name(shape_name)
            if shape is None:
                continue
            shape.set_pose_prop_from_dict(prop_dict)
            #if REL_ABS_ANCHOR_AT in prop_dict:
            #    abs_anchor_at = prop_dict[REL_ABS_ANCHOR_AT].copy()
            #    abs_anchor_at.translate(anchor_at.x, anchor_at.y)
            #    shape.move_to(abs_anchor_at.x, abs_anchor_at.y)
        if self.custom_props:
            self.custom_props.apply_props()
        self.readjust_sizes()
        self.perform_post_create_from_xml()

    def set_pose_prop_from_dict(self, prop_dict, non_direct_props=None):
        super(MultiShape, self).set_pose_prop_from_dict(
            prop_dict, non_direct_props=["pose"])

    def set_shape_prop_for_all_poses(self, shape, prop_name):
        for pose_name, pose in self.poses.items():
            old_prop_dict = pose[shape.get_name()]
            current_shape_prop_dict = shape.get_pose_prop_dict()
            if prop_name in old_prop_dict:
                old_prop_dict[prop_name] = current_shape_prop_dict[prop_name]

    def set_pose_transition(self, start_pose, end_pose, value):
        start_pose = self.poses.get(start_pose)
        end_pose = self.poses.get(end_pose)
        if not start_pose or not end_pose:
            return
        anchor_at = self.anchor_at.copy()
        for shape_name, start_prop_dict in start_pose.items():
            if shape_name not in end_pose.keys(): continue
            shape = self.shapes.get_item_by_name(shape_name)
            if shape is None:
                continue
            end_prop_dict = end_pose[shape_name]
            shape.set_transition_pose_prop_from_dict(start_prop_dict, end_prop_dict, frac=value)
            """
            if REL_ABS_ANCHOR_AT not in start_prop_dict or \
               REL_ABS_ANCHOR_AT not in end_prop_dict:
                continue
            start_rel_abs_anchor_at = start_prop_dict[REL_ABS_ANCHOR_AT].copy()
            end_rel_abs_anchor_at = end_prop_dict[REL_ABS_ANCHOR_AT].copy()
            abs_anchor_at = Point(0, 0)
            abs_anchor_at.set_inbetween(start_rel_abs_anchor_at, end_rel_abs_anchor_at, value)
            abs_anchor_at.translate(anchor_at.x, anchor_at.y)
            shape.move_to(abs_anchor_at.x, abs_anchor_at.y)
            """
        if self.custom_props:
            self.custom_props.apply_props()
        self.readjust_sizes()
        self.perform_post_create_from_xml()

    def get_pose_list(self, interior_shape=None):
        if interior_shape:
            shape = self.get_interior_shape(interior_shape)
            if shape:
                return shape.get_pose_list()
        poses = [[None, ""]]
        for pose_name in sorted(self.poses.keys()):
            poses.append([self.get_pose_pixbuf(pose_name), pose_name])
        return poses

    def get_new_timeline(self, time_line_class):
        i = len(self.timelines)
        while(True):
            i += 1
            time_line_name = "TimeLine_{0:03}".format(i)
            if time_line_name not in self.timelines:
                break
        time_line = time_line_class(name=time_line_name, multi_shape=self)
        self.timelines[time_line_name] = time_line
        return time_line

    def rename_timeline(self, old_timeline_name, new_timeline_name):
        if new_timeline_name in self.timelines: return False
        timeline = self.timelines[old_timeline_name]
        self.timelines[new_timeline_name] = timeline
        del self.timelines[old_timeline_name]
        timeline.set_name(new_timeline_name)
        return True

    def delete_timeline(self, timeline_name):
        if timeline_name not in self.timelines: return False
        del self.timelines[timeline_name]
        return True

    def get_timelines_model(self):
        model = []
        for name in sorted(self.timelines.keys()):
            time_line = self.timelines[name]
            model.append(["{0} [{1:.2f} sec]".format(name, time_line.duration), name])
        return model

    def add_custom_prop(self, prop_name, prop_type):
        if hasattr(self, prop_name):
            return False
        if hasattr(self, "get_" + prop_name):
            return False
        if hasattr(self, "set_" + prop_name):
            return False
        if prop_name.find("tm_") == 0:
            return False
        if prop_name == "internal":
            return False
        if self.custom_props is None:
            self.custom_props = CustomProps()
        self.custom_props.add_prop(prop_name, prop_type)
        return True

    def remove_custom_prop(self, prop_name):
        if self.custom_props is None:
            return
        self.custom_props.remove_prop(prop_name)

    def get_custom_prop(self, prop_name):
        if not self.custom_props:
            return None
        return self.custom_props.get_prop(prop_name)

    def set_width(self, value, fixed_anchor=True):
        pass
        #multi shape's width is controlled by its content

    def set_height(self, value, fixed_anchor=True):
        pass
        #multi shape's width is controlled by its content

    def has_prop(self, prop_name):
        if not super(MultiShape, self).has_prop(prop_name):
            return self.custom_props and self.custom_props.has_prop(prop_name)
        return True

    def get_prop_value(self, prop_name):
        get_attr_name = "get_" + prop_name
        if hasattr(self, get_attr_name):
            return getattr(self, get_attr_name)()
        elif hasattr(self, prop_name):
            return getattr(self, prop_name)
        elif self.custom_props:
            return self.custom_props.get_prop_value(prop_name)
        return None

    def get_prop_type(self, prop_name):
        if self.custom_props and self.custom_props.has_prop(prop_name):
            custom_prop = self.custom_props.get_prop(prop_name)
            if custom_prop.prop_type == CustomProp.PropTypes["color"]:
                return "number_list"
        return super(MultiShape, self).get_prop_type(prop_name)

    def set_camera(self, camera):
        self.camera=self.shapes.get_item_by_name(camera)

    def set_prop_value(self, prop_name, value, prop_data=None):
        if prop_name == "followed_upto":
            self.set_followed_upto(value, prop_data)
            return

        if prop_name.find("tm_") == 0:
            timeline_name = prop_name[3:]
            if timeline_name in self.timelines:
                timeline = self.timelines[timeline_name]
                timeline.move_to(timeline.duration*value)
            return
        if prop_name == "internal" or prop_name.startswith("pose_"):
            shape_name = prop_data.get("shape")
            if shape_name:
                shape = self.get_interior_shape(shape_name)
                if not shape:
                    shape = self
            else:
                shape = self
            if prop_data["type"] == "pose":
                start_pose = prop_data.get("start_pose")
                if start_pose is None:
                    start_pose = prop_data.get("start_pose_raw")
                    end_pose = prop_data.get("end_pose_raw")
                else:
                    end_pose = prop_data.get("end_pose")
                if start_pose and shape.has_poses():
                    if end_pose:
                        shape.set_pose_transition(start_pose, end_pose, value)
                    else:
                        shape.set_pose(start_pose)
                else:
                    prop_name = prop_data.get("prop_name")
                    if prop_name:
                        shape.set_prop_value(prop_name, value)
            elif prop_data["type"] == "timeline":
                if "pose" in prop_data:
                    pose = prop_data["pose"]
                    self.set_pose(pose)
                timeline_name = prop_data["timeline"]
                self.set_camera(prop_data.get("camera"))
                if timeline_name in self.timelines:
                    timeline = self.timelines[timeline_name]
                    timeline.move_to(timeline.duration*value)
            return
        set_attr_name = "set_" + prop_name
        if hasattr(self, set_attr_name):
            getattr(self, set_attr_name)(value)
        elif hasattr(self, prop_name):
            setattr(self, prop_name, value)
        elif self.custom_props:
            self.custom_props.set_prop_value(prop_name, value)

    def readjust_sizes(self):
        for shape in self.shapes:
            if isinstance(shape, CurveShape):
               shape.fit_size_to_include_all()
            elif isinstance(shape, PolygonShape):
               shape.fit_size_to_include_all()
            elif isinstance(shape, MultiShape):
               shape.readjust_sizes()

        outline = None
        for shape in self.shapes:
            if not shape.has_outline:
                continue
            shape_outline = shape.get_abs_outline(0, root_shape=self)
            if outline is None:
                outline = shape_outline
            else:
                outline.expand_include(shape_outline)

        if outline is None: return
        abs_anchor_at = self.get_abs_anchor_at()
        offset = Point(-outline.left, -outline.top)

        for shape in self.shapes:
            if shape.locked_to_shape:
                continue
            if not shape.has_outline:
                continue
            shape.shift_abs_anchor_at(offset)

        if self.locked_shapes:
            for shape in self.locked_shapes:
                if not shape.has_outline:
                    continue
                shape.shift_abs_anchor_at(offset)

        self.width = outline.width
        self.height = outline.height

        self.anchor_at.translate(offset.x, offset.y)
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def add_shape(self, shape, transform=True, resize=True):
        self.add_interior_shape(shape, self.shapes, transform=transform, lock=False)
        if resize:
            self.readjust_sizes()

    def remove_shape(self, shape, transform=True, resize=True):
        shape = self.remove_interior_shape(shape, self.shapes, transform=transform, lock=False)
        if resize:
            self.readjust_sizes()
        return shape

    def remove_all_shapes(self):
        shapes = []
        while(len(self.shapes)>0):
            shapes.append(self.remove_shape(self.shapes.get_at_index(0)))
        return shapes

    def rename_shape(self, shape, name):
        if name in ("self",):
            return False
        old_name = shape.get_name()
        if self.shapes.rename(old_name, name):
            for pose in self.poses.values():
                if old_name in pose:
                    pose[name] = pose[old_name]
                    del pose[old_name]
        return True

    def draw_path(self, ctx, for_fill=False):
        draw_rounded_rectangle(ctx, 0, 0, self.width, self.height, 0)

    @staticmethod
    def draw_shape(shape, ctx, drawing_size=None,
                         fixed_border=True, no_camera=True,
                         root_shape=None, exclude_camera_list=None,
                         pre_matrix=None, show_non_renderable=False):
        if isinstance(shape, MultiShape):
            multi_shape = shape
            if multi_shape.fill_color is not None:
                ctx.save()
                multi_shape.pre_draw(ctx, root_shape=root_shape)
                multi_shape.draw_path(ctx, for_fill=True)
                multi_shape.draw_fill(ctx)
                ctx.restore()

            renderable_shapes_count = len(multi_shape.shapes)
            masked_surface = None
            if multi_shape.masked and len(multi_shape.shapes)>1:
                renderable_shapes_count -= 1
                masked_surface = cairo.ImageSurface(
                    cairo.FORMAT_ARGB32, int(drawing_size.x), int(drawing_size.y))
                masked_ctx = cairo.Context(masked_surface)
                if pre_matrix:
                    masked_ctx.set_matrix(pre_matrix)
                orig_ctx = ctx
                ctx = masked_ctx

            if len(multi_shape.shapes)>0:
                last_shape = multi_shape.shapes.get_at_index(-1)
            else:
                last_shape = None
            for i in range(renderable_shapes_count):
                child_shape = multi_shape.shapes.get_at_index(i)
                if not child_shape.visible:
                    continue
                if not child_shape.renderable and not show_non_renderable:
                    continue
                if isinstance(child_shape, MultiShape):
                    display_non_renderable = False
                else:
                    display_non_renderable = show_non_renderable
                MultiShape.draw_shape(child_shape, ctx,
                            drawing_size = drawing_size, fixed_border=fixed_border,
                            no_camera=no_camera, exclude_camera_list=exclude_camera_list,
                            root_shape=root_shape, pre_matrix=pre_matrix,
                            show_non_renderable=display_non_renderable)

            if masked_surface:
                last_shape = multi_shape.shapes.get_at_index(-1)
                ctx = orig_ctx
                orig_mat = ctx.get_matrix()
                if pre_matrix:
                    ctx.set_matrix(cairo.Matrix())

                if last_shape.fill_color is None:
                    masking_surface = cairo.ImageSurface(
                        cairo.FORMAT_ARGB32, int(drawing_size.x), int(drawing_size.y))
                    masking_ctx = cairo.Context(masking_surface)
                    if pre_matrix:
                        masking_ctx.set_matrix(pre_matrix)
                    MultiShape.draw_shape(last_shape, masking_ctx,
                                drawing_size = drawing_size, fixed_border=fixed_border,
                                no_camera=no_camera, exclude_camera_list=exclude_camera_list,
                                root_shape=root_shape, pre_matrix=pre_matrix,
                                show_non_renderable=display_non_renderable)
                else:
                    masking_surface = None

                ctx.set_source_surface(masked_surface)
                if masking_surface:
                    ctx.mask_surface(masking_surface)
                ctx.set_matrix(orig_mat)

                if not masking_surface:
                    ctx.save()
                    last_shape.pre_draw(ctx, root_shape=root_shape)
                    last_shape.draw_path(ctx)
                    ctx.clip()
                    ctx.paint()
                    ctx.restore()
                else:
                    ctx.fill()

                if last_shape.renderable or show_non_renderable:
                    ctx.save()
                    last_shape.pre_draw(ctx, root_shape=root_shape)
                    last_shape.draw_path(ctx)
                    if fixed_border:
                        ctx.restore()
                        last_shape.draw_border(ctx)
                    else:
                        last_shape.draw_border(ctx)
                        ctx.restore()

            if multi_shape.border_color is not None:
                ctx.save()
                multi_shape.pre_draw(ctx, root_shape=root_shape)
                multi_shape.draw_path(ctx, for_fill=False)
                if fixed_border:
                    ctx.restore()
                    multi_shape.draw_border(ctx)
                else:
                    multi_shape.draw_border(ctx)
                    ctx.restore()
        elif isinstance(shape, CameraShape) and \
            (no_camera or (exclude_camera_list and shape in exclude_camera_list)):
            return

        elif isinstance(shape, CurveJoinerShape):
            shape.draw(ctx, root_shape=root_shape, fixed_border=fixed_border)

        elif isinstance(shape, DocumentShape):
            shape.draw(ctx,
                    drawing_size = drawing_size, fixed_border=fixed_border,
                    no_camera=no_camera, exclude_camera_list=exclude_camera_list,
                    root_shape=root_shape, pre_matrix=pre_matrix,
                    show_non_renderable=False)
        elif isinstance(shape, CustomShape):
            shape.draw(ctx, drawing_size = drawing_size, root_shape=root_shape,
                            fixed_border=fixed_border, pre_matrix=pre_matrix)
        elif isinstance(shape, MimicShape):
            if shape.mimic_like_shape:
                MultiShape.draw_shape(shape.mimic_like_shape, ctx,
                    drawing_size = drawing_size, fixed_border=fixed_border,
                    no_camera=no_camera, exclude_camera_list=exclude_camera_list,
                    root_shape=root_shape, pre_matrix=pre_matrix,
                    show_non_renderable=False)
        else:
            ctx.save()
            shape.pre_draw(ctx, root_shape=root_shape)
            shape.draw_path(ctx, for_fill=True)
            shape.draw_fill(ctx)
            ctx.restore()

            if isinstance(shape, ImageShape) or \
               isinstance(shape, VideoShape) or \
               isinstance(shape, AudioShape) or \
               isinstance(shape, CameraShape) or \
               isinstance(shape, ThreeDShape):
                ctx.save()
                shape.pre_draw(ctx, root_shape=root_shape)
                #shape.draw_path(ctx)
                if isinstance(shape, CameraShape):
                    shape.draw_image(ctx, fixed_border=fixed_border,
                                          exclude_camera_list=exclude_camera_list)
                elif isinstance(shape, ThreeDShape):
                    shape.draw_image(ctx, root_shape=root_shape, pre_matrix=pre_matrix)
                else:
                    shape.draw_image(ctx, root_shape=root_shape)
                ctx.restore()

            if isinstance(shape, TextShape):
                ctx.save()
                shape.pre_draw(ctx, root_shape=root_shape)
                shape.draw_path(ctx)
                shape.draw_text(ctx)
                ctx.restore()

            ctx.save()
            shape.pre_draw(ctx, root_shape=root_shape)
            shape.draw_path(ctx)
            if fixed_border:
                ctx.restore()
                shape.draw_border(ctx)
            else:
                shape.draw_border(ctx)
                ctx.restore()

    def draw(self, ctx, drawing_size=None,
                        fixed_border=True, no_camera=True,
                        root_shape=None, exclude_camera_list=None,
                        pre_matrix=None, show_non_renderable=False):

        MultiShape.draw_shape(self, ctx, drawing_size = drawing_size,
                        fixed_border=fixed_border, no_camera=no_camera,
                        root_shape=root_shape, exclude_camera_list=exclude_camera_list,
                        pre_matrix=pre_matrix, show_non_renderable=show_non_renderable)

    def be_like_shape(self, shape):
        self.width = shape.width
        self.height = shape.height
        self.anchor_at.copy_from(shape.anchor_at)

    def move_anchor_at_center(self):
        self.anchor_at.x = self.width*.5
        self.anchor_at.y = self.height*.5

    def scale_border_width(self, mult):
        for shape in self.shapes:
            if isinstance(shape, MultiShape):
                shape.scale_border_width(mult)
            else:
                shape.border_width *= mult

    def flip(self, direction):
        for shape in self.shapes:
            shape.flip(direction)
            abs_anchor_at = shape.get_abs_anchor_at()
            if direction == "x":
                abs_anchor_at.x = 2*self.anchor_at.x - abs_anchor_at.x
            elif direction == "y":
                abs_anchor_at.y = 2*self.anchor_at.y - abs_anchor_at.y
            shape.move_to(abs_anchor_at.x, abs_anchor_at.y)
        self.readjust_sizes()

    def save_shape_positions_with_order(self):
        positions = OrderedDict()
        for shape in self.shapes:
            positions.add(shape.get_name(), shape.get_stage_xy())
        self.child_shape_postions_with_order = positions

    def apply_saved_shape_positions_with_order(self):
        positions = self.child_shape_postions_with_order
        for i in range(len(positions)):
            shape_name = positions.keys[i]
            stage_xy = positions.get_item_at_index(i)
            for shape in self.shapes:
                if shape.get_name() == shape_name:
                    shape.set_stage_xy(stage_xy)
                    self.shapes.insert_at(i, shape)
        self.readjust_sizes()

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

        curve_count = len(curve_shape.curves)
        if curve_count>1:
            shape_count = len(self.shapes)
            for i in range(shape_count):
                shape = self.shapes.get_at_index(i)
                curve_index = i%curve_count
                point, angle = curve_shape.get_baked_point(self.followed_upto, curve_index=curve_index)
                point = self.transform_point(point)
                shape.move_to(point.x, point.y)
                if follow_angle:
                    self.set_angle(angle)
            self.readjust_sizes()
            self.anchor_at.x = self.width*.5
            self.anchor_at.y = self.height*.5
        else:
            point, angle = curve_shape.get_baked_point(self.followed_upto)
            self.move_to(point.x, point.y)
            if follow_angle:
                self.set_angle(angle)

    def cleanup(self):
        for shape in self.shapes:
            shape.cleanup()
        super(MultiShape, self).cleanup()
