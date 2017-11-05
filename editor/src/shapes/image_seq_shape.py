from ..commons import *
from image_shape import ImageShape
import os
from .. import settings as Settings

class ImageSeqShape(ImageShape):
    TYPE_NAME = "ImageSeq"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        super(ImageSeqShape, self).__init__(
                anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        self.image_folder = None
        self.progress = 0.

    def copy(self, copy_name=False, deep_copy=False):
        newob = ImageSeqShape(
                    self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                    copy_value(self.fill_color), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_image_folder(self.image_folder)
        newob.alpha = self.alpha
        return newob

    def get_xml_element(self):
        elm = super(ImageSeqShape, self).get_xml_element()
        del elm.attrib["image_path"]
        elm.attrib["image_folder"] = self.image_folder
        elm.attrib["alpha"] = "{0}".format(self.alpha)
        elm.attrib["progress"] = "{0}".format(self.progress)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(ImageSeqShape, cls).create_from_xml_element(elm)
        shape.alpha = float(elm.attrib.get("alpha", 1.))
        shape.progress = float(elm.attrib.get("progress", 0.))
        shape.set_image_folder(elm.attrib.get("image_folder", ""))
        return shape

    def set_image_folder(self, value):
        self.image_folder = value
        self.set_progress(self.progress)

    def set_progress(self, value):
        if value <0:
            value = 0
        value %= 1.0
        self.progress = value
        image_folder = Settings.Directory.get_full_path(self.image_folder)
        if os.path.isdir(image_folder):
            files = sorted(os.listdir(image_folder))
            index = int(len(files)*self.progress)
            self.set_image_path(os.path.join(image_folder, files[index]))
