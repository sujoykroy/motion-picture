import numpy, cairo, os
from .misc import *
from xml.etree.ElementTree import Element as XmlElement

class TextureResources(object):
    TAG_NAME = "texture"

    def __init__(self):
        self.names = []
        self.paths = []
        self.surfaces = []

    def copy(self):
        newob = TextureResources()
        for i in range(len(self.names)):
            newob.add_resource(self.names[i], self.paths[i])
        return newob

    def add_resource(self, resource_name, resource_path):
        if resource_name in self.names:
            return
        self.names.append(resource_name)
        self.paths.append(resource_path)
        if os.path.isfile(resource_path):
            surface = cairo.ImageSurface.create_from_png(resource_path)
        else:
            surface = None
        self.surfaces.append(surface)

    def add_resource_from_xml_element(self, elm):
        resource_name = elm.attrib["name"]
        resource_path = elm.attrib["path"]
        self.add_resource(resource_name, resource_path)

    def contains(self, resource_name):
        return resource_name in self.names

    def get_index(self, resource_name):
        return self.names.index(resource_name)

    def get_xml_elements(self):
        elms = []
        for i in range(len(self.names)):
            elm = XmlElement(self.TAG_NAME)
            elm.attrib["name"] = self.names[i]
            elm.attrib["path"] = self.paths[i]
            elms.append(elm)
        return elms

class TextureMapColor(object):
    COLOR_TYPE_NAME = "tx"

    def __init__(self, resources, resource_index, texcoords, built=False):
        self.resources = resources
        self.resource_index = resource_index
        self.normalized_texcoords = texcoords
        self.texcoords = list(texcoords)
        self.built = built
        for i in range(len(self.texcoords)):
            texcoords = self.texcoords[i].copy()
            if texcoords.shape[1] == 2:
                texcoords = numpy.concatenate(
                    (texcoords, numpy.array(
                        [numpy.ones(texcoords.shape[0], dtype="f")]).T), axis=1)
            self.texcoords[i] = texcoords

    def set_resources(self, resources):
        self.resources = resources

    def get_resource_name(self):
        return self.resources.names[self.resource_index]

    def to_text(self):
        arr = []
        for i in range(len(self.normalized_texcoords)):
            texcoords = self.normalized_texcoords[i]
            tarr = []
            for j in range(texcoords.shape[0]):
                coords = "{0},{1}".format(texcoords[j][0], texcoords[j][1])
                tarr.append(coords)
            arr.append(",".join(tarr))
        text = ";".join(arr)
        return self.COLOR_TYPE_NAME + ":" + "{0}".format(self.resource_index) + "/" + text

    def build(self):
        if self.built :
            return
        self.built = True
        for i in range(len(self.texcoords)):
            texcoords = self.texcoords[i]
            texcoords[:, 0] = texcoords[:, 0]*self.get_surface().get_width()
            texcoords[:, 1] = (1-texcoords[:, 1])*self.get_surface().get_height()
            self.texcoords[i] = texcoords

    def copy(self):
        newob = TextureMapColor(
            self.resources, self.resource_index,
            copy_value(self.texcoords), built=self.built)
        return newob

    def get_surface(self):
        return self.resources.surfaces[self.resource_index]

    @classmethod
    def from_text(cls, text):
        resource_index, texcoords_text = text.split("/")
        resource_index = int(resource_index)
        texcoords = texcoords_text.split(";")
        for i in range(len(texcoords)):
            texcoord = texcoords[i].split(",");
            for j in range(len(texcoord)):
                texcoord[j] = float(texcoord[j])
            texcoord = numpy.array(texcoord).reshape(-1, 2)
            texcoords[i] = texcoord
        #texcoords = numpy.array(texcoords)
        return cls(None, resource_index, texcoords)
