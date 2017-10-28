from object3d import Object3d
from point3d import Point3d
import numpy
from xml.etree.ElementTree import Element as XmlElement

class Light3d(Object3d):
    pass

class PointLight3d(Light3d):
    TAG_NAME = "point_light"

    def __init__(self, location, color):
        super(PointLight3d, self).__init__()
        self.color = color
        self.location = location
        self.rel_location_values = dict()
        self.z_depths = dict()

    def precalculate(self):
        super(PointLight3d, self).precalculate()
        self.world_point_values = self.reverse_transform_point_values(numpy.array([self.location.values]))

    def build_projection(self, camera):
        self.rel_location_values[camera] = camera.forward_transform_point_values(self.world_point_values)
        self.z_depths[camera] = self.rel_location_values[camera][0][2]

    def get_xml_element(self, ):
        elm = XmlElement(self.TAG_NAME)
        return elm

class DirectionalLight3d(PointLight3d):
    TAG_NAME = "dir_light"

    def __init__(self, location, color, normal, cone_cosine=.86, decay=1./25):
        super(DirectionalLight3d, self).__init__(location, color)
        values = normal.values[:3]/numpy.linalg.norm(normal.values[:3])
        self.normal = Point3d.create_if_needed(values)
        self.cone_cosine = cone_cosine
        self.decay = decay

    def set_normal(self, normal):
        values = normal.values[:3]/numpy.linalg.norm(normal.values[:3])
        self.normal = Point3d.create_if_needed(values)
