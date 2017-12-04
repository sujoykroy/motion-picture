from MotionPicture.commons import draw_stroke, draw_fill, Point, Polygon, Color, draw_oval
from MotionPicture.commons import ImageHelper
from MotionPicture import TextShape
import numpy
import skimage
import skimage.transform
import cairo
import time

class Drawer(object):
    def __init__(self):
        self.params = dict()
        self.params_info = dict(
            pic_shape=dict(type="text", default=""),
            poly_shape=dict(type="text", default=""),
        )
        self.use_custom_surface = False

    def set_params(self, params):
        self.params.update(params)

    def set_progress(self, value):
        self.progress = value

    def get_points_from_poly(self, poly_shape, pic_shape):
        points = numpy.zeros((0,2))

        for poly_i in range(len(poly_shape.polygons)):
            polygon = poly_shape.polygons[poly_i]
            for point_i in range(len(polygon.points)):
                point = polygon.points[point_i].copy()
                #point.scale(poly_shape.width, poly_shape.height)
                points = numpy.append(points, (point.x, point.y))

        points.shape = (-1, 2)
        mins = numpy.amin(points, axis=0)
        points = points - mins
        points = points/numpy.amax(points, axis=0)

        points = numpy.append(points, (0, 0))
        points = numpy.append(points, (1, 0))
        points = numpy.append(points, (1, 1))
        points = numpy.append(points, (0, 1))

        points.shape = (-1, 2)
        return points

    def draw(self, ctx, anchor_at, width, height, parent_shape):
        poly_shape_name = self.params.get("poly_shape")
        pic_shape_name = self.params.get("pic_shape")
        poly_shape = parent_shape.get_interior_shape(poly_shape_name)
        poly_shape = poly_shape.copy(deep_copy=True)
        pic_shape = parent_shape.get_interior_shape(pic_shape_name)
        if not poly_shape or not pic_shape:
            return
        dest_points = self.get_points_from_poly(poly_shape, pic_shape)

        poly_shape = poly_shape.copy(deep_copy=True)
        poly_shape.set_form(poly_shape.forms.keys()[0])
        start_points = self.get_points_from_poly(poly_shape, pic_shape)
        poly_shape.cleanup()

        dest_points = dest_points*((pic_shape.width, pic_shape.height))
        start_points = start_points*((pic_shape.width, pic_shape.height))

        poly_trans = skimage.transform.PolynomialTransform()
        poly_trans.estimate(start_points, dest_points)

        surface = pic_shape.get_surface(pic_shape.width, pic_shape.height, 0)
        image_surfarray = ImageHelper.surface2array(surface)
        image_surfarray = skimage.img_as_float(image_surfarray)

        tform = skimage.transform.PiecewiseAffineTransform()
        tform.estimate(dest_points, start_points)
        warped_surfarray = skimage.transform.warp(image_surfarray, tform)
        warped_surfarray = skimage.img_as_ubyte(warped_surfarray)

        surface = cairo.ImageSurface.create_for_data(
            warped_surfarray, cairo.FORMAT_ARGB32, int(pic_shape.width), int(pic_shape.height))
        ctx.translate((pic_shape.width-width)*.5, (pic_shape.height-height)*.5)
        ctx.scale(width/pic_shape.width, height/pic_shape.height)
        ctx.set_source_surface(surface)
        ctx.rectangle(0,0, width, height)
        ctx.fill()
