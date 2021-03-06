import numpy
from xml.etree.ElementTree import Element as XmlElement

from .object3d import Object3d
from .polygon3d import Polygon3d
from .point3d import Point3d
from .misc import *
from .texture_map_color import *
from .colors import *

DEFAULT_BORDER_COLOR = Color.from_html("000000")
DEFAULT_FILL_COLOR = Color.from_html("CCCCCC")
DEFAULT_BORDER_WIDTH = 1

class PolyGroup3d(Object3d):
    TAG_NAME = "polygrp3"

    def __init__(self, points, polygons,
                       kind="linear",
                       force_style=False,
                       border_color=DEFAULT_BORDER_COLOR,
                       fill_color=DEFAULT_FILL_COLOR,
                       border_width=DEFAULT_BORDER_WIDTH):
        super(PolyGroup3d, self).__init__()

        self.border_color = copy_value(border_color)
        self.fill_color = copy_value(fill_color)
        self.border_width = border_width

        self.kind = kind

        self.points = []
        for point in points:
            point = Point3d.create_if_needed(point)
            self.points.append(point)
        self.polygons = []
        for polygon in polygons:
            self.add_polygon(polygon)

        self.world_point_values = None
        self.point_projections = dict()
        self.point_indices_sorted = dict()

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        self.load_xml_elements(elm)

        point_values = []
        for point in self.points:
            point_values.append(point.to_text())
        points_elm = XmlElement("points")
        points_elm.text = ",".join(point_values);
        elm.append(points_elm)

        for polygon in self.polygons:
            elm.append(polygon.get_xml_element())
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        border_color = color_from_text(elm.attrib.get("bc", None))
        fill_color = color_from_text(elm.attrib.get("fc", None))
        border_width = elm.attrib.get("bw", None)
        if border_width is not None:
            border_width = float(border_width)

        points = [float(p) for p in elm.find("points").text.split(",")]
        points = numpy.array(points).reshape(-1, 3)

        polygons = []
        for polygon_elm in elm.findall(Polygon3d.TAG_NAME):
            polygon = Polygon3d.create_from_xml_element(polygon_elm)
            polygons.append(polygon)

        newob = cls(points=points, polygons=polygons,
                border_color=border_color, fill_color=fill_color,
                border_width=border_width)
        newob.load_from_xml_elements(elm)

        return newob

    def add_polygon(self, polygon, force_style=False):
        if not isinstance(polygon, Polygon3d):
                polygon = Polygon3d.create_if_needed(self, polygon)
                polygon.kind = self.kind
                erase_style = True
        else:
            polygon.parent = self
            erase_style = force_style

        if polygon is None:
            return
        self.polygons.append(polygon)

        if erase_style:
            polygon.border_color = None
            polygon.border_width = None
            polygon.fill_color = None
        return polygon

    def copy(self):
        points = []
        for point in self.points:
            points.append(point.copy())

        polygons = []
        for polygon in self.polygons:
            polygons.append(polygon.copy())

        newob = PolyGroup3d(
            points=points, polygons=polygons, kind=self.kind,
            border_color=copy_value(self.border_color),
            fill_color=copy_value(self.fill_color),
            border_width=self.border_width)
        self.copy_into(newob)
        return newob

    def precalculate(self):
        super(PolyGroup3d, self).precalculate()
        self.world_point_values = None
        for point in self.points:
            if self.world_point_values is None:
                self.world_point_values = numpy.array([point.values])
            else:
                self.world_point_values = numpy.concatenate(
                        (self.world_point_values, [point.values]), axis=0)
        self.world_point_values = self.reverse_transform_point_values(self.world_point_values)
        for polygon in self.polygons:
            polygon.precalculate()

    def build_projection(self, camera):
        camera_point_values = camera.forward_transform_point_values(self.world_point_values)
        self.point_projections[camera] = camera.viewer_point_values(camera_point_values)

        for polygon in self.polygons:
            polygon.build_projection(camera)

    def point_z_sort_key(self, o1, o2):
        if o1[2] == o2[2]:
            return 0
        if o1[2]>o2[2]:
            return 1
        return -1

    @classmethod
    def create_from_polygons_points(cls,
                       polygons_points, kind="linear",
                       border_color=DEFAULT_BORDER_COLOR,
                       fill_color=DEFAULT_FILL_COLOR,
                       border_width=DEFAULT_BORDER_WIDTH):
        points = []
        polygons = []
        for polygon_points in polygons_points:
            polygon_points = list(polygon_points)
            start_index = len(points)
            end_index = start_index + len(polygon_points)
            polygons.append(list(range(start_index, end_index, 1)))
            points.extend(polygon_points)
        return cls(kind=kind,
                   points=points, polygons=polygons,
                   border_color=border_color,
                   fill_color=fill_color,
                   border_width=border_width)

    @classmethod
    def create_polygon(cls,
                       points, kind="linear",
                       border_color=DEFAULT_BORDER_COLOR,
                       fill_color=DEFAULT_FILL_COLOR,
                       border_width=DEFAULT_BORDER_WIDTH):
        polygons = [list(range(len(points)))]
        return cls(kind=kind,
                   points=points, polygons=polygons,
                   border_color=border_color,
                   fill_color=fill_color,
                   border_width=border_width)
