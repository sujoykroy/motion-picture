import numpy
import tempfile

import PIL.Image

from ..geom import Rectangle

class RenderInfo:
    KEY_IMAGE_RAW = 'image_raw'
    KEY_IMAGE_SHAPE = 'image_shape'
    KEY_EDITABLE_RECT = 'edtiable_rect'
    KEY_ORIG_IMG_SCALE = 'orig_img_scale'

    def __init__(self, image, editable_rect=None, orig_image_scale=1):
        self._image = image
        self._editable_rect = editable_rect
        self.orig_image_scale = orig_image_scale

    @property
    def image(self):
        return self._image

    @property
    def editable_rect(self):
        if not self._editable_rect:
            return Rectangle(0, 0, self.image.width, self.image.height)
        return self._editable_rect

    def get_json(self):
        data = {}
        image_data = numpy.array(self._image, dtype=numpy.uint8)
        data[self.KEY_IMAGE_RAW] = image_data.tostring()
        data[self.KEY_IMAGE_SHAPE] = image_data.shape
        if self._editable_rect:
            data[self.KEY_EDITABLE_RECT] = self._editable_rect.get_json()
        data[self.KEY_ORIG_IMG_SCALE] = self.orig_image_scale
        return data

    @classmethod
    def create_from_json(cls, data):
        image_data = numpy.fromstring(data[cls.KEY_IMAGE_RAW], dtype=numpy.uint8)
        image_data = image_data.reshape(data[cls.KEY_IMAGE_SHAPE])
        image = PIL.Image.fromarray(image_data)

        edit_rect_data = data.get(cls.KEY_EDITABLE_RECT)
        editable_rect = None
        if edit_rect_data:
            editable_rect = Rectangle.create_from_json(edit_rect_data)
        return cls(image, editable_rect, data[cls.KEY_ORIG_IMG_SCALE])
