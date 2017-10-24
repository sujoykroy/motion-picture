from object3d import Object3d
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

