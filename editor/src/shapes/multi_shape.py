from ..commons import *
from shape import Shape
from shape_list import ShapeList
from rectangle_shape import RectangleShape
from oval_shape import OvalShape
from ring_shape import RingShape
from curve_shape import CurveShape
from polygon_shape import PolygonShape
from image_shape import ImageShape
from video_shape import VideoShape
from audio_shape import AudioShape
from text_shape import TextShape
from camera_shape import CameraShape
from threed_shape import ThreeDShape
from ..time_lines import MultiShapeTimeLine
from xml.etree.ElementTree import Element as XmlElement
from custom_props import *

class MultiShapePoseRenderer(object):
    def __init__(self, multi_shape, pose_name):
        self.multi_shape = multi_shape
        self.pose_name = pose_name

    def get_name(self):
        return self.pose_name

    def get_id(self):
        return self.pose_name

    def get_pixbuf(self):
        multi_shape = self.multi_shape.copy(deep_copy=True)
        multi_shape.set_pose_raw(multi_shape.get_pose_by_name(self.pose_name))
        multi_shape.reset_transformations()
        multi_shape.parent_shape = None
        pixbuf = multi_shape.get_pixbuf(64, 64)
        return pixbuf

class MultiShape(Shape):
    TYPE_NAME = "multi_shape"
    POSE_TAG_NAME = "pose"
    POSE_SHAPE_TAG_NAME = "pose_shape"

    def __init__(self, anchor_at=None, border_color=Color(0,0,0,1),
                        border_width=1, fill_color=None, width=1, height=1):
        if anchor_at is None:
            anchor_at = Point(width*.5, height*.5)
        Shape.__init__(self,  anchor_at, border_color, border_width, fill_color, width, height)
        self.shapes = ShapeList()
        self.poses = dict()
        self.timelines = dict()
        self.masked = False
        self.custom_props = None

    def copy_data_from_linked(self):
        if not self.linked_to: return

        diff_point = self.anchor_at.diff(self.linked_to.anchor_at)
        self.shapes.clear()

        for shape in  self.linked_to.shapes:
            shape_abs_anchor_at = shape.get_abs_anchor_at()
            shape = shape.copy(copy_name=True, deep_copy=True)
            shape.parent_shape=self
            shape.move_to(shape_abs_anchor_at.x + diff_point.x,
                          shape_abs_anchor_at.y + diff_point.y)
            self.shapes.add(shape)
        self.readjust_sizes()
        self.poses = copy_dict(self.linked_to.poses)
        self.timelines.clear()
        for key, timeline in self.linked_to.timelines.items():
            self.timelines[key] = timeline.copy()

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        if self.masked:
            elm.attrib["masked"] = "True"
        for shape in self.shapes:
            elm.append(shape.get_xml_element())

        for pose_name, pose in self.poses.items():
            pose_elm = XmlElement(self.POSE_TAG_NAME)
            pose_elm.attrib["name"] = pose_name
            for shape_name, prop_dict in pose.items():
                pose_shape_elm = XmlElement(self.POSE_SHAPE_TAG_NAME)
                pose_shape_elm.attrib["name"] = shape_name
                for prop_name, value in prop_dict.items():
                    if prop_name in ("form_raw",):
                        pose_shape_elm.append(value.get_xml_element())
                    else:
                        if hasattr(value, "to_text"):
                            value = value.to_text()
                        pose_shape_elm.attrib[prop_name] = "{0}".format(value)
                pose_elm.append(pose_shape_elm)
            elm.append(pose_elm)

        for timeline in self.timelines.values():
            elm.append(timeline.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
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
                child_shape = MultiShape.create_from_xml_element(shape_element)
            elif shape_type == ThreeDShape.TYPE_NAME:
                child_shape = ThreeDShape.create_from_xml_element(shape_element)
            if child_shape is None: continue
            child_shape.parent_shape = shape
            shape.shapes.add(child_shape)

        for pose_elm in elm.findall(cls.POSE_TAG_NAME):
            pose_name = pose_elm.attrib["name"]
            pose = dict()
            for pose_shape_elm in pose_elm.findall(cls.POSE_SHAPE_TAG_NAME):
                prop_dict = dict()
                shape_name = None
                for prop_name, value in pose_shape_elm.attrib.items():
                    if prop_name == "name":
                        shape_name = value
                        continue
                    if prop_name in ("anchor_at", "translation", "abs_anchor_at", "rel_abs_anchor_at"):
                        value = Point.from_text(value)
                    elif prop_name in ("fill_color", "border_color"):
                        value = color_from_text(value)
                    elif prop_name == "pre_matrix":
                        value = Matrix.from_text(value)
                    else:
                        try:
                            value = float(value)
                        except ValueError:
                            continue
                    prop_dict[prop_name] = value
                form = pose_shape_elm.find(CurvesForm.TAG_NAME)
                if form:
                    prop_dict["form_raw"] = CurvesForm.create_from_xml_element(form)
                if shape_name:
                    pose[shape_name] = prop_dict
            shape.poses[pose_name] = pose

        for time_line_elm in elm.findall(MultiShapeTimeLine.TAG_NAME):
            time_line = MultiShapeTimeLine.create_from_xml_element(time_line_elm, shape)
            shape.timelines[time_line.name] = time_line
        return shape

    def copy(self, copy_name=False, copy_shapes=True, deep_copy=False):
        newob = MultiShape(anchor_at=self.anchor_at.copy(), width=self.width, height=self.height)
        Shape.copy_into(self, newob, copy_name=copy_name)
        if copy_shapes or deep_copy:
            for shape in self.shapes:
                child_shape = shape.copy(copy_name=True, deep_copy=deep_copy)
                child_shape.parent_shape = newob
                newob.shapes.add(child_shape)
        if deep_copy:
            newob.poses = copy_dict(self.poses)
            for key, timeline in self.timelines.items():
                newob.timelines[key] = timeline.copy()
        newob.masked = self.masked
        if self.custom_props:
            newob.custom_props = self.custom_props.copy()
        return newob

    def save_pose(self, pose_name):
        if not pose_name:
            i = len(self.poses)
            while(True):
                i += 1
                pose_name = "Pose_{0:03}".format(i)
                if pose_name not in self.poses:
                    break

        self.poses[pose_name] = self.get_pose_raw()
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
            rel_abs_anchor_at = shape.get_abs_anchor_at()
            rel_abs_anchor_at.translate(-anchor_at.x, -anchor_at.y)
            prop_dict["rel_abs_anchor_at"] = rel_abs_anchor_at
        return pose

    def rename_pose(self, old_pose_name, new_pose_name):
        if new_pose_name in self.poses: return False
        pose = self.poses[old_pose_name]
        self.poses[new_pose_name] = pose
        del self.poses[old_pose_name]
        return True

    def delete_pose(self, pose_name):
        del self.poses[pose_name]

    def set_pose(self, pose_name):
        if pose_name not in self.poses: return
        self.set_pose_raw(self.poses[pose_name])

    def set_pose_raw(self, pose):
        anchor_at = self.anchor_at.copy()
        for shape_name, prop_dict in pose.items():
            shape = self.shapes[shape_name]
            shape.set_pose_prop_from_dict(prop_dict)
            if "rel_abs_anchor_at" in prop_dict:
                abs_anchor_at = prop_dict["rel_abs_anchor_at"].copy()
                abs_anchor_at.translate(anchor_at.x, anchor_at.y)
                shape.move_to(abs_anchor_at.x, abs_anchor_at.y)
        self.readjust_sizes()

    def set_shape_prop_for_all_poses(self, shape, prop_name):
        for pose in self.poses.values():
            old_prop_dict = pose[shape.get_name()]
            current_shape_prop_dict = shape.get_pose_prop_dict()
            if prop_name in old_prop_dict:
                old_prop_dict[prop_name] = current_shape_prop_dict[prop_name]

    def set_pose_transition(self, start_pose, end_pose, value):
        start_pose = self.poses[start_pose]
        end_pose = self.poses[end_pose]
        anchor_at = self.anchor_at.copy()
        for shape_name, start_prop_dict in start_pose.items():
            if shape_name not in end_pose.keys(): continue
            shape = self.shapes[shape_name]
            end_prop_dict = end_pose[shape_name]
            shape.set_transition_pose_prop_from_dict(start_prop_dict, end_prop_dict, frac=value)
            start_rel_abs_anchor_at = start_prop_dict["rel_abs_anchor_at"].copy()
            end_rel_abs_anchor_at = end_prop_dict["rel_abs_anchor_at"].copy()
            abs_anchor_at = Point(0, 0)
            abs_anchor_at.set_inbetween(start_rel_abs_anchor_at, end_rel_abs_anchor_at, value)
            abs_anchor_at.translate(anchor_at.x, anchor_at.y)
            shape.move_to(abs_anchor_at.x, abs_anchor_at.y)
        self.readjust_sizes()

    def get_pose_list(self):
        poses = []
        for pose_name in sorted(self.poses.keys()):
            pose = MultiShapePoseRenderer(self, pose_name)
            poses.append(pose)
        return poses

    def get_new_timeline(self):
        i = len(self.timelines)
        while(True):
            i += 1
            time_line_name = "TimeLine_{0:03}".format(i)
            if time_line_name not in self.timelines:
                break
        time_line = MultiShapeTimeLine(name=time_line_name, multi_shape=self)
        self.timelines[time_line_name] = time_line
        return time_line

    def rename_timeline(self, old_timeline_name, new_timeline_name):
        if new_timeline_name in self.timelines: return False
        timeline = self.timelines[old_timeline_name]
        self.timelines[new_timeline_name] = timeline
        del self.timelines[old_timeline_name]
        return True

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

    def has_prop(self, prop_name):
        if not super(MultiShape, self).has_prop(prop_name):
            return self.custom_props and self.custom_props.get_prop(prop_name) is not None
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

    def set_prop_value(self, prop_name, value, prop_data=None):
        if prop_name.find("tm_") == 0:
            timeline_name = prop_name[3:]
            if timeline_name in self.timelines:
                timeline = self.timelines[timeline_name]
                timeline.move_to(timeline.duration*value)
            return
        if prop_name == "internal":
            if prop_data["type"] == "pose":
                start_pose = prop_data["start_pose"]
                end_pose = prop_data["end_pose"]
                if end_pose:
                    self.set_pose_transition(start_pose, end_pose, value)
                else:
                    self.set_pose(start_pose)
            elif prop_data["type"] == "timeline":
                if "pose" in prop_data:
                    pose = prop_data["pose"]
                    self.set_pose(pose)
                timeline_name = prop_data["timeline"]
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

    def add_shape(self, shape, transform=True, resize=True):
        if self.shapes.contain(shape): return
        if transform:
            shape_abs_anchor_at = shape.get_abs_anchor_at()

            rel_shape_abs_anchor_at = self.transform_point(shape_abs_anchor_at)
            shape.move_to(rel_shape_abs_anchor_at.x, rel_shape_abs_anchor_at.y)
            #if self.get_angle() == 0:
            #    shape.set_angle(shape.get_angle()-self.get_angle())
            #else:
            #    shape.pre_angle -= self.get_angle()
        shape.parent_shape = self

        self.shapes.add(shape)
        if resize:
            self.readjust_sizes()

    def readjust_sizes(self):
        outline = None
        for shape in self.shapes:
            shape_outline = shape.get_abs_outline(0)
            if outline is None:
                outline = shape_outline
            else:
                outline.expand_include(shape_outline)

        if outline is None: return
        abs_anchor_at = self.get_abs_anchor_at()
        offset_x = -outline.left
        offset_y = -outline.top

        for shape in self.shapes:
            shape_abs_anchor_at = shape.get_abs_anchor_at()
            shape_abs_anchor_at.translate(offset_x, offset_y)
            shape.move_to(shape_abs_anchor_at.x, shape_abs_anchor_at.y)

        self.width = outline.width
        self.height = outline.height

        self.anchor_at.x += offset_x
        self.anchor_at.y += offset_y
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def build_matrix(self):
        matrix = cairo.Matrix()
        matrix.rotate(self.angle*RAD_PER_DEG)
        matrix.scale(self.post_scale_x, self.post_scale_y)
        return matrix

    def remove_shape(self, shape, resize=True):
        abs_outline = shape.get_abs_outline(0)
        shape_abs_anchor_at = shape.get_abs_anchor_at()
        old_translation_point = shape.translation.copy()
        new_translation_point = self.reverse_transform_point(old_translation_point)
        angle = shape.get_angle()+self.get_angle()

        point = self.reverse_transform_point(shape.get_abs_anchor_at())
        if self == shape.parent_shape:
            shape.parent_shape = None

        if shape.pre_matrix:
            shape.prepend_pre_matrix(self.build_matrix())
        else:
            if self.get_angle()==0:
                if abs(shape.get_angle())>0:
                    shape.scale_x *= self.post_scale_x
                    shape.scale_y *= self.post_scale_y
                else:
                    shape.set_width(shape.width*self.post_scale_x)
                    shape.set_height(shape.height*self.post_scale_y)
                    shape.anchor_at.scale(self.post_scale_x, self.post_scale_y)
            else:
                if self.post_scale_x != 1 or self.post_scale_y != 1:
                    shape.prepend_pre_matrix(self.build_matrix())
                else:
                    shape.set_angle(angle)
        shape.move_to(point.x, point.y)

        self.shapes.remove(shape)
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

    def draw(self, ctx, drawing_size=None,
                        fixed_border=True, no_camera=True,
                        root_shape=None, exclude_camera_list=None):
        if self.masked and len(self.shapes)>1:#masking feature needs to be revisited.
            last_shape = self.shapes.get_at_index(-1)
            if not isinstance(last_shape, MultiShape):
                for i in range(len(self.shapes)-1):
                    shape = self.shapes.get_at_index(i)
                    masked_surface = cairo.ImageSurface(
                            cairo.FORMAT_ARGB32, int(drawing_size.x), int(drawing_size.y))
                    masked_ctx = cairo.Context(masked_surface)
                    if isinstance(shape, MultiShape):
                        shape.draw(masked_ctx, drawing_size, fixed_border)
                    else:
                        shape.draw(masked_ctx, fixed_border)

                    ctx.set_source_surface(masked_surface)
                    ctx.save()
                    last_shape.pre_draw(ctx, root_shape=root_shape)
                    last_shape.draw_path(ctx)
                    ctx.clip()
                    ctx.paint()
                    ctx.restore()

                ctx.save()
                last_shape.pre_draw(ctx, root_shape=root_shape)
                last_shape.draw_path(ctx)
                if fixed_border:
                    ctx.restore()
                    last_shape.draw_border(ctx)
                else:
                    last_shape.draw_border(ctx)
                    ctx.restore()
                return

        for shape in self.shapes:
            if not shape.visible:
                continue
            if isinstance(shape, CameraShape) and \
                (no_camera or (exclude_camera_list and shape in exclude_camera_list)):
                continue
            if isinstance(shape, MultiShape):
                shape.draw(ctx, drawing_size, fixed_border, root_shape=root_shape)
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
                    shape.draw_path(ctx)
                    if isinstance(shape, CameraShape):
                        shape.draw_image(ctx, fixed_border=fixed_border,
                                              exclude_camera_list=exclude_camera_list)
                    else:
                        shape.draw_image(ctx)
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
