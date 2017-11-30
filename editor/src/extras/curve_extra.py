from .. import Document
from .. shapes import RectangleShape
from ..commons import Point
import numpy

def get_path_xy_values(doc_filename, path_shape_name,
                       time_divs, line_divs,
                       curve_shape_name = u"curve", path_time_line_name=u"lines"):
    (doc_width, doc_height), main_container_shape = Document.load_and_get_main_multi_shape(doc_filename)

    doc_shape = RectangleShape(
            anchor_at=Point(doc_width*.5, doc_height*.5),
            border_color = None,
            border_width = 0,
            fill_color= None,
            width = doc_width, height = doc_width, corner_radius=0)
    main_container_shape.parent_shape = doc_shape

    xy_values = numpy.zeros((0, 0, 3), dtype="float")
    path_shape = main_container_shape.get_interior_shape(path_shape_name)
    if not path_shape:
        return xy_values

    curve_shape = path_shape.get_interior_shape(curve_shape_name)
    path_lines = path_shape.timelines.get(path_time_line_name)
    if not path_lines or not curve_shape:
        return xy_values

    path_width = int(path_shape.width)
    path_height = int(path_shape.height)

    for ti in xrange(time_divs):
        tfrac = ti*1./time_divs
        path_lines.move_to(path_lines.duration*tfrac)
        prev_point = None
        for li in xrange(line_divs):
            lfrac = (li+1)*1./line_divs
            point, angle = curve_shape.get_baked_point(frac=lfrac)
            point = path_shape.reverse_transform_locked_shape_point(
                    point, root_shape=doc_shape)
            point.translate(-doc_shape.anchor_at.x, -doc_shape.anchor_at.y)
            xy_values = numpy.append(xy_values, (point.x, point.y, angle))

    xy_values.shape = (time_divs, line_divs, -1)

    Document.unload_file(doc_filename)
    return xy_values
