from MotionPicture.commons import draw_stroke, draw_fill, Point3d,PolyGroup3d, Point, Color, PointLight3d
from MotionPicture.commons import Container3d
from MotionPicture.shapes import ThreeDShape
from MotionPicture import MultiShapeModule
import math
import cairo
import numpy

class Drawer(object):
    def __init__(self):
        self.params = dict()
        points = []

        x_div = y_div = 50
        x_spread = y_spread = 10
        y_spread = 100


        xs = numpy.linspace(-x_spread*5, x_spread*.5, num=x_div, endpoint=True)
        ys = numpy.linspace(-y_spread*.5, y_spread*.5, num=y_div, endpoint=True)
        xs, ys = numpy.meshgrid(xs, ys, indexing="ij")
        grid = numpy.vstack((xs.flatten(), ys.flatten()))
        grid = numpy.concatenate((grid, [numpy.zeros(grid.shape[1])]), axis=0)
        grid = grid.T
        grid.shape = (x_div, y_div, 3)
        self.grid_points = grid + numpy.array([0,0,0])

        xs = numpy.arange(0, x_div)
        ys = numpy.arange(0, y_div)
        xs, ys = numpy.meshgrid(xs, ys, indexing="ij")
        grid = numpy.vstack((xs.flatten(), ys.flatten()))
        grid = grid.T
        grid.shape = (x_div, y_div, 2)
        self.grid_indices = grid
        points = []
        polygons = []
        for xi in xrange(x_div):
            for yi in xrange(y_div):
                xyz = self.grid_points[xi, yi,:]
                point = Point3d(xyz[0], xyz[1], xyz[2])
                points.append(point)

        self.mesh3d = PolyGroup3d(points=points, polygons=[])
        for xi in xrange(x_div):
            polygon = self.mesh3d.add_polygon(list(range(xi*y_div, (xi+1)*y_div)))
            polygon.closed = False
            polygon.fill_color = None

        indices = self.find_indices(Point3d(10,0,0), 20)
        self.obj3d = Container3d()
        #self.obj3d.append(self.mesh3d)

        #self.write_points(self.grid_indices.reshape(-1,2))

        #self.obj3d.fill_color =  Color.from_html("CCCCCC")#None
        self.mesh3d.fill_color = None#Color.from_html("FF0000")

        self.lights = []
        self.lights.append(PointLight3d(location=Point3d(0, 0, -300), color=Color.from_html("00FF00")))
        self.lights.append(PointLight3d(location=Point3d(0,0, 300), color=Color.from_html("0000FF")))

        self.init_grid_points = self.grid_points.copy()

    def write_points(self, indices):
        for i in xrange(indices.shape[0]):
            xi = indices[i][0]
            yi = indices[i][1]
            c = xi*self.grid_points.shape[0]+yi
            self.mesh3d.points[c].values[:3] = self.grid_points[xi, yi,:]

    def find_indices(self, point, distance):
        dist_grid = numpy.linalg.norm(self.grid_points-point.values[:3], axis=2)
        cond = (dist_grid<=distance)
        cond.shape = self.grid_points.shape[:2]
        indices = self.grid_indices[cond]
        return indices

    def set_params(self, params):
        self.params = dict(params)

    def set_progress(self, value):
        self.progress = value
        self.grid_points = self.init_grid_points.copy()
        for dis in xrange(1,30):
            indices = self.find_indices(Point3d(-20,0,0), dis)
            xi, yi = indices[:,0], indices[:,1]
            self.grid_points[xi, yi, 2] = self.grid_points[xi, yi, 2]+(1*self.progress)
        self.write_points(self.grid_indices.reshape(-1,2))

    def draw(self, ctx, anchor_at, width, height, parent_shape):
        shape_name = self.params.get("shape_name", "\\3d").decode("utf-8")
        if not shape_name:
            return
        shape3d = parent_shape.get_interior_shape(shape_name)
        if not shape3d:
            return
        shape3d.d3_object.clear()# = self.obj3d
        shape3d.d3_object.append(self.mesh3d)
        for light in self.lights:
            shape3d.d3_object.append(light)
        shape3d.should_rebuild_d3 = True
        shape3d.should_rebuild_camera = True
