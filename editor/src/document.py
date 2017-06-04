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

import moviepy.editor as movie_editor
import numpy

class Document(object):
    def __init__(self, filename=None, width=400., height=300.):
        self.filename = filename
        self.width = width
        self.height = height
        self.main_multi_shape = None
        self.guides = []
        self.reundo = TaskManager()
        self.fixed_border = True
        if self.filename:
            self.load_from_xml_file()
        if not self.main_multi_shape:
            self.main_multi_shape = MultiShape(width=width, height=height, border_color=None)
            self.main_multi_shape._name = "MainShape"
        self.main_multi_shape.border_color = None
        self.main_multi_shape.fill_color = None
        self.main_multi_shape.border_width = 0

    def is_empty(self):
        return not self.filename and self.reundo.is_empty()

    def get_main_multi_shape(self):
        return self.main_multi_shape

    def get_shape_by_name(self, name):
        return self.main_multi_shape.shapes.get_item_by_name(name)

    def get_camera_names(self):
        names= []
        for shape in self.main_multi_shape.shapes:
            if isinstance(shape, CameraShape):
                names.append(shape.get_name())
        return names

    def get_shape_at_hierarchy(self, names):
        multi_shape = self.main_multi_shape
        shape = None
        for i in range(len(names)):
            name = names[i]
            if i == 0:
                 if multi_shape.get_name() == name:
                    shape = multi_shape
                 else:
                    break
            else:
                shape = shape.shapes.get_item_by_name(name)
                if not shape:
                    break
        return shape

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
        self.fixed_border = (doc.attrib.get("fixed_border", "") != "False")

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
        if not self.fixed_border:
            doc.attrib["fixed_border"] = "False"
        root.append(doc)

        for guide in self.guides:
            root.append(guide.get_xml_element())

        tree = XmlTree(root)
        root.append(self.main_multi_shape.get_xml_element())
        self.add_linked_clone_elements(self.main_multi_shape, root)

        backup_file = None
        if filename is None:
            filename = self.filename

        if filename is not None:
            self.filename = filename
            if os.path.isfile(filename):
                backup_file = filename + ".bk"
                os.rename(filename, backup_file)

        #tree.write(self.filename)
        try:
            tree.write(self.filename)
        except TypeError as e:
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

    def get_surface(self, width, height, bg_color=True):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        ctx = cairo.Context(surface)
        if bg_color:
            ctx.rectangle(0, 0, width, height)
            ctx.set_source_rgb(1,1,1)
            ctx.fill()
        ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

        shape = self.main_multi_shape
        scale = min(width*1./self.width, height*1./self.height)
        ctx.translate((width-scale*self.width)*.5, (height-scale*self.height)*.5)
        ctx.scale(scale, scale)
        set_default_line_style(ctx)
        shape.draw(ctx, Point(self.width, self.height), self.fixed_border)
        return ctx.get_target()

    def get_pixbuf(self, width, height, bg_color=True):
        surface= self.get_surface(width, height, bg_color)
        pixbuf= Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())
        return pixbuf

    def get_rgb_array(self, camera):
        if camera:
            width, height = camera.width, camera.height
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(camera.width), int(camera.height))
            ctx = cairo.Context(surface)
            ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
            ctx.rectangle(0, 0, width, height)
            ctx.set_source_rgb(1,1,1)
            ctx.fill()
            camera.paint_screen(ctx, camera.width, camera.height, cam_scale=1.)
        else:
            width, height = self.width, self.height
            surface= self.get_surface(width, height)
        data = surface.get_data()
        rgb_array = 0+numpy.frombuffer(surface.get_data(), numpy.uint8)
        rgb_array.shape = (height, width, 4)
        rgb_array = rgb_array[:,:,[2,1,0,3]]
        rgb_array = rgb_array[:,:, :3]
        return rgb_array

    def make_movie(self, filename, time_line, start_time=0, end_time=None,
                         fps=24, camera=None, ffmpeg_params=None, codec=None, audio=True):
        timelines = self.main_multi_shape.timelines
        if not timelines:
            return
        if time_line is None:
            time_line = timelines.values()[0]

        elif not isinstance(time_line, MultiShapeTimeLine):
            if time_line in timelines:
                time_line = timelines[time_line]

        if not time_line:
            return

        if end_time is None:
            end_time = time_line.duration

        if camera:
            camera = self.get_shape_by_name(camera)

        frame_maker = FrameMaker(self, time_line, start_time, end_time, camera)
        video_clip = movie_editor.VideoClip(frame_maker.make_frame, duration=frame_maker.get_duration())

        if audio:
            audio_clips = time_line.get_audio_clips()
            if audio_clips:
                audio_clip = movie_editor.CompositeAudioClip(audio_clips)
                video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(
            filename, fps=fps, codec=codec, preset="superslow", ffmpeg_params=ffmpeg_params,
            bitrate="320k")

    @staticmethod
    def create_image(icon_name, scale=None):
        filename = os.path.join(Settings.ICONS_FOLDER, icon_name + ".xml")
        doc = Document(filename=filename)
        if scale:
            doc.main_multi_shape.scale_border_width(scale)
        pixbuf = doc.get_pixbuf(width=20, height=20, bg_color=False)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        image.set_tooltip_text(get_displayble_prop_name(icon_name))
        return image

    @staticmethod
    def get_icon_shape(icon_name, width=None, height=None):
        filename = os.path.join(Settings.ICONS_FOLDER, icon_name + ".xml")
        doc = Document(filename=filename)
        shape = doc.main_multi_shape

        if width is not None and height is not None:
            scale_x = width/shape.get_width()
            scale_y = height/shape.get_height()

            shape.anchor_at.x=0
            shape.anchor_at.y=0

            shape.scale_border_width(min(scale_x, scale_y))
            shape.set_prop_value("scale_x", scale_x)
            shape.set_prop_value("scale_y", scale_y)

            shape.move_to(0,0)
        return shape

class FrameMaker(object):
    def __init__(self, doc, time_line, start_time, end_time, camera):
        self.doc = doc
        self.time_line = time_line
        self.start_time = start_time
        self.end_time = end_time
        self.camera = camera

    def get_duration(self):
        return self.end_time-self.start_time

    def make_frame(self, t):
        self.time_line.move_to(t+self.start_time)
        return self.doc.get_rgb_array(self.camera)
