import numpy
from misc import *

class TextureMapColor(object):
    Surfaces = dict()

    def __init__(self, resource_name, texcoords, built=False):
        self.resource_name = resource_name
        self.texcoords = texcoords
        self.built = built
        for i in range(len(self.texcoords)):
            texcoords = self.texcoords[i]
            if texcoords.shape[1] == 2:
                texcoords = numpy.concatenate(
                    (texcoords, numpy.array(
                        [numpy.ones(texcoords.shape[0], dtype="f")]).T), axis=1)
                self.texcoords[i] = texcoords

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
        newob = TextureMapColor(self.resource_name, copy_value(self.texcoords), built=self.built)
        return newob

    def get_surface(self):
        return TextureMapColor.Surfaces[self.resource_name]
