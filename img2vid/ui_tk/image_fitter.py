"""This module holds class to handle editable region of slide image."""

from types import SimpleNamespace

import PIL.ImageTk

from ..geom import Point, Rectangle
from ..renderer import ImageRenderer

class ImageFitter:
    """This class provide editable area of slide image.
    User makes cropping rectangle on slide image.
    Forward and reverse transformation for usch rectangles are
    performed by this class.

    :ivar RenderInfo: render_info

    """
    def __init__(self):
        self.render_info = None
        self.canvas_size = Point(0, 0)

        self.rects = SimpleNamespace()
        self.rects.image = Rectangle(0, 0, 0, 0)
        self.rects.screen = Rectangle(0, 0, 0, 0)
        self.rects.editable = Rectangle(0, 0, 0, 0)

        self.orig_image_scale = 1
        self.image_tk = None

    def build_screen_area(self, width, height, screen_config, auto_fit=True):
        """Builds dimension of screen area where image will be squeezed to show."""
        self.canvas_size.assign(width, height)

        scale = min(
            width/screen_config.width, height/screen_config.height)
        if scale == 0:
            self.rects.screen.set_values(0, 0, 0, 0)
            return
        screen_width = int(screen_config.width*scale)
        screen_height = int(screen_config.height*scale)

        screen_left = int((width-screen_width)*0.5)
        screen_top = int((height-screen_height)*0.5)

        self.rects.screen.set_values(
            x1=screen_left,
            y1=screen_top,
            x2=screen_left+screen_width,
            y2=screen_top+screen_height)
        if auto_fit:
            self.fit()

    def fit(self, build_tk=True):
        """Fit the render_info.image in canvas rectangle"""
        if not self.render_info:
            return
        if self.canvas_size.x == 0:
            return

        image = self.render_info.image
        width = self.rects.screen.width
        height = int(image.height*width/image.width)

        if height > self.rects.screen.height:
            height = self.rects.screen.height
            width = int(image.width*height/image.height)

        self.orig_image_scale = width/image.width
        self.rects.editable.copy_from(self.render_info.editable_rect)
        self.rects.editable.same_scale(self.orig_image_scale)

        image = ImageRenderer.resize(image, width, height)
        left = int((self.canvas_size.x-width)*0.5)
        top = int((self.canvas_size.y-height)*0.5)

        self.rects.image.set_values(
            x1=left, y1=top,
            x2=left+width, y2=top+height)

        self.rects.editable.translate(
            Point(self.rects.image.x1, self.rects.image.y1))
        if build_tk:
            self.image_tk = PIL.ImageTk.PhotoImage(image=image)

    def reverse_transform_rect(self, rect):
        """Returns the reversed transfomed version of given rectangle"""
        rect = rect.copy()
        rect.translate(
            Point(self.rects.editable.x1, self.rects.editable.y1), sign=-1)
        rect.scale(1/self.rects.editable.width, 1/self.rects.editable.height)
        rect.scale(
            self.render_info.editable_rect.width,
            self.render_info.editable_rect.height)
        rect.same_scale(1/self.render_info.orig_image_scale)
        return rect
