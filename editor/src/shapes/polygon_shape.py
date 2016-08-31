from ..commons import *
from shape import Shape
from xml.etree.ElementTree import Element as XmlElement

class PolygonShape(Shape):
    TYPE_NAME = "polygon_shape"
    FORM_TAG_NAME = "form"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height):
        Shape.__init__(self, anchor_at, border_color, border_width, fill_color, width, height)
        self.polygons = []
        self.forms = dict()

    def save_form(self, form_name):
        if form_name is None:
            i = len(self.forms)
            while True:
                i += 1
                form_name = "Form_{0}".format(i)
                if form_name not in self.forms:
                    break
        polygons = []
        anchor_at = self.anchor_at.copy()
        anchor_at.scale(1./self.width, 1./self.height)
        for polygon in self.polygons:
            polygon = polygon.copy()
            for point in polygon.points:
                point.translate(-anchor_at.x, -anchor_at.y)
            polygons.append(polygon)
        form_dict = dict()
        form_dict["polygons"] = polygons
        form_dict["width"] = self.width
        form_dict["height"] = self.height
        self.forms[form_name] = dict(form_dict)
        return form_name

    def set_form(self, form_name):
        form_dict = self.forms[form_name]

        diff_width = form_dict["width"] - self.width
        diff_height = form_dict["height"] - self.height
        abs_anchor_at = self.get_abs_anchor_at()

        self.width = form_dict["width"]
        self.height = form_dict["height"]
        form_polygons = form_dict["polygons"]

        anchor_at = self.anchor_at.copy()
        anchor_at.scale(1./self.width, 1./self.height)

        for i in range(min(len(form_polygons), len(self.polygons))):
            self_polygon = self.polygons[i]
            form_polygon = form_polygons[i]
            for j in range(min(len(self_polygon.points), len(form_polygon.points))):
                self_point = self_polygon.points[j]
                form_point = form_polygon.points[j]
                self_point.copy_from(form_point)
                self_point.translate(anchor_at.x, anchor_at.y)

        self.fit_size_to_include_all()
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)

    def set_prop_value(self, prop_name, value, prop_data=None):
        if prop_name == "internal":
            start_form = prop_data["start_form"]
            end_form = prop_data["end_form"]

            if end_form is None or end_form not in self.forms:
                self.set_form(start_form)
                return

            start_form_dict = self.forms[start_form]
            end_form_dict = self.forms[end_form]

            new_width = start_form_dict["width"] +  \
                        (end_form_dict["width"]-start_form_dict["width"])*value
            new_height = start_form_dict["height"] + \
                        (end_form_dict["height"]-start_form_dict["height"])*value

            diff_width = new_width - self.width
            diff_height = new_height - self.height

            abs_anchor_at = self.get_abs_anchor_at()

            self.width = new_width
            self.height = new_height
            start_form_polygons = start_form_dict["polygons"]
            end_form_polygons = end_form_dict["polygons"]

            anchor_at = self.anchor_at.copy()
            anchor_at.scale(1./self.width, 1./self.height)

            for i in range(min(len(start_form_polygons), len(end_form_polygons), len(self.polygons))):
                self_polygon = self.polygons[i]
                start_form_polygon = start_form_polygons[i]
                end_form_polygon = end_form_polygons[i]

                for j in range(min(len(self_polygon.points), len(start_form_polygon.points), \
                                   len(end_form_polygon.points))):
                    self_point = self_polygon.points[j]
                    start_form_point = start_form_polygon.points[j]
                    end_form_point = end_form_polygon.points[j]

                    self_point.set_inbetween(start_form_point, end_form_point, value)
                    self_point.translate(anchor_at.x, anchor_at.y)

            self.fit_size_to_include_all()
            self.move_to(abs_anchor_at.x, abs_anchor_at.y)
        else:
            Shape.set_prop_value(self, prop_name, value, prop_data)

    def rename_form(self, old_form, new_form):
        if new_form in self.forms: return
        self.forms[new_form] = self.forms[old_form]
        del self.forms[old_form]

    def get_xml_element(self):
        elm = Shape.get_xml_element(self)
        for polygon in self.polygons:
            elm.append(polygon.get_xml_element())

        for form_name, form in self.forms.items():
            form_elm = XmlElement(self.FORM_TAG_NAME)
            form_elm.attrib["name"] = form_name
            form_elm.attrib["width"] = "{0}".format(form["width"])
            form_elm.attrib["height"] = "{0}".format(form["height"])
            for polygon in form["polygons"]:
                form_elm.append(polygon.get_xml_element())
            elm.append(form_elm)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        shape = cls(*arr)
        default_point = Point(0,0)

        for polygon_elm in elm.findall(Polygon.TAG_NAME):
            polygon = Polygon.create_from_xml_element(polygon_elm)
            shape.polygons.append(polygon)

        for form_elm in elm.findall(cls.FORM_TAG_NAME):
            form_name = form_elm.attrib["name"]
            form_dict = dict()
            form_dict["width"] = float(form_elm.attrib["width"])
            form_dict["height"] = float(form_elm.attrib["height"])
            form_dict["polygons"] = polygons = []
            for polygon_elm in form_elm.findall(Polygon.TAG_NAME):
                polygons.append(Polygon.create_from_xml_element(polygon_elm))
            shape.forms[form_name] = form_dict

        shape.assign_params_from_xml_element(elm)
        return shape

    def copy(self, copy_name=False):
        newob = PolygonShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                            self.fill_color.copy(), self.width, self.height)
        self.copy_into(newob, copy_name)
        for polygon in self.polygons:
            newob.polygons.append(polygon.copy())
        return newob

    def add_polygon(self, polygon):
        self.polygons.append(polygon)
        self.fit_size_to_include_all()

    def _draw_polygon(self, ctx, polygon):
        ctx.save()
        ctx.scale(self.width, self.height)
        polygon.draw_path(ctx)
        ctx.restore()

    def draw_path(self, ctx, for_fill=False):
        paths = []
        for polygon in self.polygons:
            if not for_fill or (for_fill and polygon.closed):
                self._draw_polygon(ctx, polygon)
                paths.append(ctx.copy_path())
        ctx.new_path()
        for path in paths:
            ctx.append_path(path)

    def fit_size_to_include_all(self):
        outline = None
        for polygon in self.polygons:
            if outline is None:
                outline = polygon.get_outline()
            else:
                outline.expand_include(polygon.get_outline())
        if not outline: return
        abs_anchor_at = self.get_abs_anchor_at()
        self.anchor_at.translate(-self.width*outline.left, -self.height*outline.top)
        self.move_to(abs_anchor_at.x, abs_anchor_at.y)
        self.set_width(outline.width*self.width)
        self.set_height(outline.height*self.height)

        if outline.height==0:
            sy = None
        else:
            sy = 1/outline.height
        if outline.width==0:
            sx = None
        else:
            sx = 1/outline.width

        for polygon in self.polygons:
            polygon.translate(-outline.left, -outline.top)
            if sx is not None and sy is not None:
                polygon.scale(sx, sy)

    def find_point_location(self, point):
        point = point.copy()
        point.scale(1./self.width, 1./self.height)
        for polygon_index in range(len(self.polygons)):
            polygon = self.polygons[polygon_index]
            found = polygon.get_closest_point(point, self.width, self.height)
            if found:
                point_index, t = found
                return (polygon_index, point_index, t)
        return None

    def insert_point_at(self, point):
        found = self.find_point_location(point)
        if not found: return False
        polygon_index, point_index, t = found
        polygon = self.polygons[polygon_index]
        polygon.insert_point_at(point_index, t)
        return True

    def insert_break_at(self, polygon_index, point_index):
        if polygon_index>=len(self.polygons): return False
        prev_polygon = self.polygons[polygon_index]
        if point_index>= len(prev_polygon.points): return False
        if prev_polygon.closed:
            #Just open up the closed polygon
            prev_polygon.closed = False
            for i in range(0, point_index, 1):
                prev_polygon.points.append(prev_polygon.points[0])
                del prev_polygon.points[0]
            prev_polygon.points.append(prev_polygon.points[0].copy())
            return True

        point = prev_polygon.points[point_index]
        new_polygon = Polygon(points=[point.copy()])
        new_polygon.points.extend(prev_polygon.points[point_index+1:])
        del prev_polygon.points[point_index+1:]
        prev_polygon.closed = False

        self.polygons.insert(polygon_index+1, new_polygon)
        return True

    def join_points(self, polygon_index_1, is_start_1, polygon_index_2, is_start_2):
        if polygon_index_1>=len(self.polygons): return False
        if polygon_index_1>=len(self.polygons): return False

        polygon_1 = self.polygons[polygon_index_1]
        polygon_2 = self.polygons[polygon_index_2]

        if polygon_index_1 == polygon_index_2:
            if is_start_1 != is_start_2:
                polygon_1.closed = True
                if abs(polygon_1.points[0].distance(polygon_1.points[-1])*self.width)<10:
                    polygon_1.points[0].x = (polygon_1.points[0].x+polygon_1.points[-1].x)*.5
                    polygon_1.points[0].y = (polygon_1.points[0].y+polygon_1.points[-1].y)*.5
                    del polygon_1.points[-1]
                return True
            return False
        if polygon_1.closed: return False
        if polygon_2.closed: return False

        dist_lapse = .01
        if is_start_1 == is_start_2:#reverse polygon_2
            rev_polygon = Polygon(points=list(reversed(polygon_2.points)))
            for pi in range(len(rev_polygon.points)):
                polygon_2.points[pi].copy_from(rev_polygon.points[pi])

        if is_start_1:#swap polygons
            polygon_1, polygon_2 = polygon_2, polygon_1
            polygon_index_1, polygon_index_2 = polygon_index_2, polygon_index_1

        #polygon_2 get attached at the end of polygon_1
        polygon_1.points[-1].x = (polygon_1.points[-1].x +  polygon_2.points[0].x)*.5
        polygon_1.points[-1].y = (polygon_1.points[-1].y +  polygon_2.points[0].y)*.5

        polygon_1.points.extend(polygon_2.points)
        del self.polygons[polygon_index_2]
        return True

    def delete_point_at(self, polygon_index, point_index):
        if polygon_index>=len(self.polygons): return False
        polygon = self.polygons[polygon_index]
        if point_index>=len(polygon.points): return False
        if len(polygon.points)<3: return False
        del polygon.points[point_index]
        if len(polygon.points)<3:
            polygon.closed=False

        self.fit_size_to_include_all()
        return True

    def extend_point(self, polygon_index, is_start):
        if polygon_index>=len(self.polygons): return False
        polygon = self.polygons[polygon_index]
        if polygon.closed: return False

        if is_start:
            polygon.points.insert(0, polygon.points[0].copy())
        else:
            polygon.points.append(polygon.points[-1].copy())
        return True
