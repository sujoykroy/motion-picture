from ..commons import *
from shape import Shape
from shape_list import ShapeList
from rectangle_shape import RectangleShape
from oval_shape import OvalShape
from curve_shape import CurveShape
from polygon_shape import PolygonShape
from image_shape import ImageShape
from ..time_lines import MultiShapeTimeLine
from xml.etree.ElementTree import Element as XmlElement

class ShapePose(object):
    def __init__(self):
        self.params = dict()

class MultiShape(Shape):
    TYPE_NAME = "multi_shape"
    POSE_TAG_NAME = "pose"
    POSE_SHAPE_TAG_NAME = "pose_shape"

    def __init__(self, anchor_at=None, border_color=Color(0,0,0,1),
                        border_width=1, fill_color=None, width=1, height=1):
        if anchor_at is None:
            anchor_at = Point(width*.5, height*.5)
        Shape.__init__(self,  anchor_at, border_color, border_width, fill_color, width, height)
        self.child_scale_x = 1.
        self.child_scale_y = 1.
        self.shapes = ShapeList()
        self.poses = dict()
        self.timelines = dict()

    @classmethod
    def get_pose_prop_names(cls):
        prop_names = Shape.get_pose_prop_names()
        prop_names.append("child_scale_x")
        prop_names.append("child_scale_y")
        return prop_names

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        elm.attrib["child_scale_x"] = "{0}".format(self.child_scale_x)
        elm.attrib["child_scale_y"] = "{0}".format(self.child_scale_y)
        for shape in self.shapes:
            elm.append(shape.get_xml_element())

        for pose_name, pose in self.poses.items():
            pose_elm = XmlElement(self.POSE_TAG_NAME)
            pose_elm.attrib["name"] = pose_name
            for shape_name, prop_dict in pose.items():
                pose_shape_elm = XmlElement(self.POSE_SHAPE_TAG_NAME)
                pose_shape_elm.attrib["name"] = shape_name
                for prop_name, value in prop_dict.items():
                    if isinstance(value, Point):
                        value = value.to_text()
                    elif isinstance(value, Color):
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

        shape.child_scale_x = float(elm.attrib.get("child_scale_x", 1.))
        shape.child_scale_y = float(elm.attrib.get("child_scale_y", 1.))

        for shape_element in elm.findall(Shape.TAG_NAME):
            shape_type = shape_element.attrib.get("type", None)
            child_shape = None
            if shape_type == RectangleShape.TYPE_NAME:
                child_shape = RectangleShape.create_from_xml_element(shape_element)
            elif shape_type == OvalShape.TYPE_NAME:
                child_shape = OvalShape.create_from_xml_element(shape_element)
            elif shape_type == CurveShape.TYPE_NAME:
                child_shape = CurveShape.create_from_xml_element(shape_element)
            elif shape_type == PolygonShape.TYPE_NAME:
                child_shape = PolygonShape.create_from_xml_element(shape_element)
            elif shape_type == MultiShape.TYPE_NAME:
                child_shape = MultiShape.create_from_xml_element(shape_element)
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
                    if prop_name in ("anchor_at, translation"):
                        value = Point.from_text(value)
                    elif prop_name in ("fill_color", "border_color"):
                        value = Color.from_text(value)
                    else:
                        value = float(value)
                    prop_dict[prop_name] = value
                if shape_name:
                    pose[shape_name] = prop_dict
            shape.poses[pose_name] = pose

        for time_line_elm in elm.findall(MultiShapeTimeLine.TAG_NAME):
            time_line = MultiShapeTimeLine.create_from_xml_element(time_line_elm, shape)
            shape.timelines[time_line.name] = time_line
        return shape

    def copy(self, copy_name=False, copy_shapes=True):
        newob = MultiShape(anchor_at=self.anchor_at.copy(), width=self.width, height=self.height)
        Shape.copy_into(self, newob, copy_name=copy_name)
        newob.child_scale_x = self.child_scale_x
        newob.child_scale_y = self.child_scale_y
        if copy_shapes:
            for shape in self.shapes:
                child_shape = shape.copy(copy_name=True)
                child_shape.parent_shape = newob
                newob.shapes.add(child_shape)
        return newob

    def save_pose(self, pose_name):
        if not pose_name:
            i = len(self.poses)
            while(True):
                i += 1
                pose_name = "Pose_{0:03}".format(i)
                if pose_name not in self.poses:
                    break

        pose = dict()
        anchor_at = self.anchor_at
        for shape in self.shapes:
            prop_dict = shape.get_pose_prop_dict()
            pose[shape.get_name()] = prop_dict
            tpoint = prop_dict["translation"]
            tpoint.translate(-anchor_at.x, -anchor_at.y)

        self.poses[pose_name] = pose
        return pose_name

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
        pose = self.poses[pose_name]
        anchor_at = self.anchor_at.copy()
        for shape_name, prop_dict in pose.items():
            shape = self.shapes[shape_name]
            shape.set_pose_prop_from_dict(prop_dict)
            tpoint = shape.translation
            tpoint.translate(anchor_at.x, anchor_at.y)
        self.readjust_sizes()

    def set_pose_transition(self, start_pose, end_pose, value):
        start_pose = self.poses[start_pose]
        end_pose = self.poses[end_pose]
        anchor_at = self.anchor_at.copy()
        for shape_name, start_prop_dict in start_pose.items():
            if shape_name not in end_pose.keys(): continue
            shape = self.shapes[shape_name]
            end_prop_dict = end_pose[shape_name]
            shape.set_transition_pose_prop_from_dict(start_prop_dict, end_prop_dict, frac=value)
            tpoint = shape.translation
            tpoint.translate(anchor_at.x, anchor_at.y)
        self.readjust_sizes()

    def get_new_timeline(self):
        i = len(self.timelines)
        while(True):
            i += 1
            time_line_name = "TimeLine_{0:03}".format(i)
            if time_line_name not in self.timelines:
                break
        time_line = MultiShapeTimeLine(name=time_line_name)
        self.timelines[time_line_name] = time_line
        return time_line

    def rename_timeline(self, old_timeline_name, new_timeline_name):
        if new_timeline_name in self.timelines: return False
        timeline = self.timelines[old_timeline_name]
        self.timelines[new_timeline_name] = timeline
        del self.timelines[old_timeline_name]
        return True

    def set_prop_value(self, prop_name, value, prop_data=None):
        if prop_name == "internal":
            if prop_data["type"] == "pose":
                start_pose = prop_data["start_pose"]
                end_pose = prop_data["end_pose"]
                if end_pose:
                    self.set_pose_transition(start_pose, end_pose, value)
                else:
                    self.set_pose(start_pose)
            elif prop_data["type"] == "timeline":
                pose = prop_data["pose"]
                timeline_name = prop_data["timeline"]
                timeline = self.timelines[timeline_name]
                self.set_pose(pose)
                timeline.move_to(timeline.duration*value)
            return
        set_attr_name = "set_" + prop_name
        if hasattr(self, set_attr_name):
            getattr(self, set_attr_name)(value)
        elif hasattr(self, prop_name):
            setattr(self, prop_name, value)

    def add_shape(self, shape):
        if self.shapes.contain(shape): return
        shape_abs_anchor_at = shape.get_abs_anchor_at()

        rel_shape_abs_anchor_at = self.transform_point(shape_abs_anchor_at)
        shape.set_angle(shape.get_angle()-self.get_angle())
        shape.move_to(rel_shape_abs_anchor_at.x, rel_shape_abs_anchor_at.y)
        shape.parent_shape = self

        self.shapes.add(shape)
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


    def remove_shape(self, shape):
        if self == shape.parent_shape:
            shape.parent_shape = None

        abs_anchor_at = self.get_abs_anchor_at()
        points = [shape.get_abs_anchor_at()]
        for point in points:
            point.translate(-self.anchor_at.x, -self.anchor_at.y)
            point.rotate_coordinate(-self.angle)
            point.translate(abs_anchor_at.x, abs_anchor_at.y)

        shape.set_angle(shape.get_angle()+self.get_angle())
        shape.move_to(points[0].x, points[0].y)

        self.shapes.remove(shape)
        self.readjust_sizes()
        return shape

    def remove_all_shapes(self):
        shapes = []
        while(len(self.shapes)>0):
            shapes.append(self.remove_shape(self.shapes.get_at_index(0)))
        return shapes

    def rename_shape(self, shape, name):
        return self.shapes.rename(shape, name)

    def set_width(self, width):
        if width <= 0: return
        self._scale_shapes(width*1.0/ self.width, 1.0)
        self.width = width

    def set_height(self, height):
        if height <= 0: return
        self._scale_shapes(1.0, height*1.0/self.height)
        self.height = height

    def _scale_shapes(self, xmult, ymult):
        self.child_scale_x *= xmult
        self.child_scale_y *= ymult
        for shape in self.shapes:
            shape.translation.x *= xmult
            shape.translation.y *= ymult

    def draw(self, ctx):
        for shape in self.shapes:
            if isinstance(shape, MultiShape):
                shape.draw(ctx)
            else:
                ctx.save()
                shape.pre_draw(ctx)
                shape.draw_path(ctx)
                ctx.restore()
                shape.draw_fill(ctx)

                if isinstance(shape, ImageShape):
                    ctx.save()
                    shape.pre_draw(ctx)
                    shape.draw_path(ctx)
                    shape.draw_image(ctx)
                    ctx.restore()

                ctx.save()
                shape.pre_draw(ctx)
                shape.draw_path(ctx)
                ctx.restore()
                shape.draw_border(ctx)

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
