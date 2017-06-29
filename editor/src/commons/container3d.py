from object3d import Object3d
from polygon3d import Polygon3d
from polygroup3d import PolyGroup3d
from texture_map_color import TextureMapColor

from colors import Color
from texture_map_color import *

import os, numpy, cairo
import collada
from xml.etree.ElementTree import Element as XmlElement

class Container3d(Object3d):
    TAG_NAME = "container3d"

    def __init__(self):
        super(Container3d, self).__init__()
        self.items = []
        self.item_names = []

    def get_item_count(self):
        return len(self.items)

    def get_xml_element(self, exclude_border_fill=False):
        elm = XmlElement(self.TAG_NAME)
        self.load_xml_elements(elm, exclude_border_fill=exclude_border_fill)
        for i in range(len(self.items)):
            item = self.items[i]
            item_elm = item.get_xml_element()
            item_elm.attrib["name"] = self.item_names[i]
            elm.append(item_elm)
        return elm

    @classmethod
    def create_from_xml_element(self, elm):
        newob = Container3d()
        newob.load_from_xml_elements(elm)
        texture_resources = newob.get_texture_resources()
        for polygroup_elm in elm.findall(PolyGroup3d.TAG_NAME):
            item = PolyGroup3d.create_from_xml_element(polygroup_elm)
            newob.append(item, name=polygroup_elm.attrib["name"])
            for polygon in item.polygons:
                if isinstance(polygon.fill_color, TextureMapColor):
                    polygon.fill_color.set_resources(texture_resources)
        return newob

    def copy(self):
        newob = Container3d()
        self.copy_into(newob)
        texture_resources = newob.get_texture_resources()
        for i in range(len(self.items)):
            item = self.items[i].copy()
            newob.append(item, self.item_names[i])
            for polygon in item.polygons:
                if isinstance(polygon.fill_color, TextureMapColor):
                    polygon.fill_color.set_resources(texture_resources)
        newob.item_names = list(self.item_names)
        return newob

    def split(self):
        newobs = []
        for i in range(len(self.items)):
            newob = Container3d()
            self.copy_into(newob)
            texture_resources = newob.get_texture_resources()
            item = self.items[i].copy()
            newob.append(item, self.item_names[i])
            for polygon in item.polygons:
                if isinstance(polygon.fill_color, TextureMapColor):
                    polygon.fill_color.set_resources(texture_resources)
            newobs.append(newob)
        return newobs

    def clear(self):
        del self.items[:]
        del self.item_names[:]

    def append(self, item, name=None):
        self.items.append(item)
        self.item_names.append(name)
        item.parent = self

    def remove(self, item):
        index = self.items.index(item)
        del self.items[index]
        del self.item_names[index]

    def precalculate(self):
        super(Container3d, self).precalculate()
        for item in self.items:
            item.precalculate()

    def __getitem__(self, index):
        if isinstance(index, str):
            if index in self.item_names:
                index = self.item_names.index(index)
            else:
                return None
        return self.items[index]

    def build_projection(self, camera):
        for item in self.items:
            item.build_projection(camera)

    def load_from_file(self, filepath, item_names=None):
        filename, file_extension = os.path.splitext(filepath)
        if item_names and isinstance(item_names, str):
            item_names = item_names.strip()
            item_names = item_names.split(",")
        if file_extension == ".dae":
            self.load_from_collada(filepath, item_names=item_names)

    def load_from_collada(self, filepath, scale=1, item_names=None):
        mesh = collada.Collada(filepath)
        geometries = dict()

        if self.texture_resources is None:
            self.texture_resources = TextureResources()
        for geometry in mesh.geometries:
            points = None
            polygons = []
            point_count = 0
            for primitive in geometry.primitives:
                for item in primitive:
                    fill_color = None
                    if item.material:
                        diffuse = mesh.materials[item.material].effect.diffuse
                        if isinstance(diffuse, tuple):
                            fill_color = Color(diffuse[0], diffuse[1], diffuse[2], 1)
                        elif isinstance(diffuse, collada.material.Map):
                            image_path= diffuse.sampler.surface.image.path
                            if not self.texture_resources.contains(image_path):
                                rpath = os.path.join(os.path.dirname(filepath), image_path)
                                rpath = rpath.replace("%20", " ")
                                self.texture_resources.add_resource(image_path, rpath)

                            fill_color = TextureMapColor(
                                self.texture_resources,
                                self.texture_resources.get_index(image_path),
                                item.texcoords)

                    polygon = [list(item.indices+point_count), fill_color]
                    polygons.append(polygon)
                if points is None:
                    points = primitive.vertex*scale
                else:
                    points = numpy.concatenate((points, primitive.vertex*scale), axis=0)
                point_count = points.shape[0]
            geometries[geometry.name] = (points, polygons)

        for scene in mesh.scenes:
            for node in scene.nodes:
                transform = node.transforms[0].matrix
                for child in node.children:
                    if isinstance(child, collada.scene.GeometryNode):
                        name = child.geometry.name
                        if item_names and node.id not in item_names:
                            continue
                        points, polygons_data = geometries[name]
                        polygons = []
                        for i in range(len(polygons_data)):
                            polygon_indices, fill_color = polygons_data[i]
                            polygon = Polygon3d(
                                    parent=None, border_width=None,
                                    border_color=None,
                                    point_indices=polygon_indices,
                                    fill_color=fill_color, closed=True)
                            polygons.append(polygon)
                        polygroup3d = PolyGroup3d(
                            points=points, polygons=polygons,
                            border_color=None, border_width=None, fill_color=None)
                        polygroup3d.extra_reverse_matrix = transform
                        self.append(polygroup3d, node.id)

