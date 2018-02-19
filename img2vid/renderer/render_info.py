from ..geom import Rectangle

class RenderInfo:
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
