import xml.etree.ElementTree as ET
from xml.etree.ElementTree import dump as XmlDump
from xml.etree.ElementTree import ElementTree as XmlTree
from xml.etree.ElementTree import Element as XmlElement

from gi.repository import Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
import cairo, os

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

    def set_doc_size(self, width, height):
        self.width = width
        self.height = height
        self.main_multi_shape.move_to(width*.5, height*.5)

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
        self.read_linked_clone_element(root)

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
        self.add_linked_clone_elements(self.main_multi_shape, root)

        backup_file = None
        if filename is not None:
            self.filename = filename
            if os.path.isfile(filename):
                backup_file = filename + ".bk"
                os.rename(filename, backup_file)
        try:
            tree.write(self.filename)
        except:
            if backup_file:
                os.rename(backup_file, filename)
                backup_file = None

        if backup_file:
            os.remove(backup_file)

    def add_linked_clone_elements(self, multi_shape, root):
        for shape in multi_shape.shapes:
            if shape.linked_clones:
                linked = XmlElement("linked")
                linked.attrib["source"] = ".".join(get_hierarchy_names(shape))
                for linked_clone_shape in shape.linked_clones:
                    linked_clone = XmlElement("dest")
                    linked_clone.text = ".".join(get_hierarchy_names(linked_clone_shape))
                    linked.append(linked_clone)
                root.append(linked)
            if isinstance(shape, MultiShape):
                self.add_linked_clone_elements(shape, root)

    def read_linked_clone_element(self, root):
        for linked_elem in root.findall("linked"):
            source = linked_elem.attrib.get("source", "")
            source_shape = get_shape_at_hierarchy(self.main_multi_shape, source.split("."))
            if not source_shape:
                continue
            for linked_clone_element in linked_elem.findall("dest"):
                linked_clone_name = linked_clone_element.text.split(".")
                linked_shape = get_shape_at_hierarchy(self.main_multi_shape, linked_clone_name)
                if not linked_shape:
                    continue
                linked_shape.set_linked_to(source_shape)
                linked_shape.copy_data_from_linked()

    def get_pixbuf(self, width, height):
        pixbuf = Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, width, height)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(), pixbuf.get_height())
        ctx = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(ctx, pixbuf, 0, 0)
        ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

        shape = self.main_multi_shape
        scale = min(width*1./self.width, height*1./self.height)
        ctx.translate((width-scale*self.width)*.5, (height-scale*self.height)*.5)
        ctx.scale(scale, scale)
        set_default_line_style(ctx)
        shape.draw(ctx, Point(self.width, self.height))

        surface= ctx.get_target()
        pixbuf= Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())

        return pixbuf

    @staticmethod
    def create_image(icon_name, scale=None):
        filename = os.path.join(Settings.ICONS_FOLDER, icon_name + ".xml")
        doc = Document(filename=filename)
        if scale:
            doc.main_multi_shape.scale_border_width(scale)
        pixbuf = doc.get_pixbuf(width=20, height=20)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        image.set_tooltip_text(get_displayble_prop_name(icon_name))
        return image
