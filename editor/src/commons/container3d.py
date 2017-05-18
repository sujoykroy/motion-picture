from object3d import Object3d
from polygon3d import Polygon3d
from polygroup3d import PolyGroup3d
from texture_map_color import TextureMapColor

from colors import Color

import os, numpy, cairo
import collada

class Container3d(Object3d):
    def __init__(self):
        super(Container3d, self).__init__()
        self.items = []
        self.item_names = []

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

    def load_from_file(self, filepath):
        filename, file_extension = os.path.splitext(filepath)
        if file_extension == ".dae":
            self.load_from_collada(filepath)

    def load_from_collada(self, filepath, scale=1):
        mesh = collada.Collada(filepath)
        geometries = dict()
        resources = dict()
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
                            image_path=diffuse.sampler.surface.image.path
                            resources[image_path] = image_path
                            fill_color = TextureMapColor(image_path, item.texcoords)
                    polygon = [list(item.indices+point_count), fill_color]
                    polygons.append(polygon)
                if points is None:
                    points = primitive.vertex*scale
                else:
                    points = numpy.concatenate((points, primitive.vertex*scale), axis=0)
                point_count = points.shape[0]
            geometries[geometry.name] = (points, polygons)

        effected_resources = dict()
        for key in resources:
            rpath = os.path.join(os.path.dirname(filepath), resources[key])
            rpath = rpath.replace("%20", " ")
            if os.path.isfile(rpath):
                TextureMapColor.Surfaces[key] = cairo.ImageSurface.create_from_png(rpath)
        for scene in mesh.scenes:
            for node in scene.nodes:
                transform = node.transforms[0].matrix
                for child in node.children:
                    if isinstance(child, collada.scene.GeometryNode):
                        name = child.geometry.name
                        points, polygons_data = geometries[name]
                        polygons = []
                        for i in range(len(polygons_data)):
                            polygon_indices, fill_color = polygons_data[i]
                            polygon = Polygon3d(
                                    parent=None,
                                    point_indices=polygon_indices,
                                    fill_color=fill_color, closed=True)
                            polygons.append(polygon)
                        polygroup3d = PolyGroup3d(points=points, polygons=polygons)
                        polygroup3d.extra_reverse_matrix = transform
                        self.append(polygroup3d, node.id)
