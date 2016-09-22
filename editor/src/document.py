import xml.etree.ElementTree as ET
from xml.etree.ElementTree import dump as XmlDump
from xml.etree.ElementTree import ElementTree as XmlTree
from xml.etree.ElementTree import Element as XmlElement

from gi.repository import Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
import cairo

import settings as Settings
from commons import *
from shapes import *
from editors.guides import Guide
from tasks import TaskManager

class Document(object):
    def __init__(self, filename=None, width=400., height=300.):
        self.filename = filename
        self.width = width
        self.height = height
        self.main_multi_shape = None
        self.guides = []
        self.reundo = TaskManager()
        if self.filename:
            self.load_from_xml_file()
        if not self.main_multi_shape:
            self.main_multi_shape = MultiShape(width=width, height=height, border_color="000000")
            self.main_multi_shape._name = "MainShape"

    def is_empty(self):
        return not self.filename and self.reundo.is_empty()

    def get_main_multi_shape(self):
        return self.main_multi_shape

    def load_from_xml_file(self):
        try:
            tree = ET.parse(self.filename)
        except IOError as e:
            return
        except ET.ParseError as e:
            return
        root = tree.getroot()
        app = root.find("app")
        if app is None or app.attrib.get("name", None) != Settings.APP_NAME: return False

        doc = root.find("doc")
        width = doc.attrib.get("width", self.width)
        height = doc.attrib.get("height", self.height)

        self.width = float(width)
        self.height = float(height)

        shape_element = root.find(Shape.TAG_NAME)
        shape_type = shape_element.attrib.get("type", None)
        if shape_type == MultiShape.TYPE_NAME:
            self.main_multi_shape = MultiShape.create_from_xml_element(shape_element)

        for guide_element in root.findall(Guide.TAG_NAME):
            guide = Guide.create_from_xml_element(guide_element)
            if guide:
                self.guides.append(guide)

    def save(self, filename=None):
        root = XmlElement("root")

        app = XmlElement("app")
        app.attrib["name"] = "{0}".format(Settings.APP_NAME)
        app.attrib["version"] = "{0}".format(Settings.APP_VERSION)
        root.append(app)

        doc = XmlElement("doc")
        doc.attrib["width"] = "{0}".format(self.width)
        doc.attrib["height"] = "{0}".format(self.height)
        root.append(doc)

        for guide in self.guides:
            root.append(guide.get_xml_element())

        tree = XmlTree(root)
        root.append(self.main_multi_shape.get_xml_element())

        if filename is not None:
            self.filename = filename
        tree.write(self.filename)


    def get_pixbuf(self, width, height):
        pixbuf = Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, width, height)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(), pixbuf.get_height())
        ctx = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, 0, 0)
        ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

        shape = self.main_multi_shape
        #ctx.scale(width*1./self.width, height*1./self.height)
        scale = min(width*1./self.width, height*1./self.height)
        ctx.translate((width-scale*self.width)*.5, (height-scale*self.height)*.5)
        ctx.scale(scale, scale)
        shape.draw(ctx)

        surface= ctx.get_target()
        pixbuf= Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())

        return pixbuf
