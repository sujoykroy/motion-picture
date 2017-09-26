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
from commons.guides import Guide
from tasks import TaskManager
from time_lines import MultiShapeTimeLine

import moviepy.editor as movie_editor
import numpy
import time
import fnmatch
import re
import multiprocessing

class Document(object):
    IdSeed = 0
    FFMPEG_PARAMS = "-quality good -qmin 10 -qmax 42"
    BIT_RATE = "640k"
    CODEC = "libvpx"

    def __init__(self, filename=None, width=400., height=300.):
        self.filename = Settings.Directory.get_full_path(filename)
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
        self.id_num = Document.IdSeed
        Document.IdSeed += 1
        Settings.Directory.add_new(filename)

    def __eq__(self, other):
        return isinstance(other, Document) and other.id_num == self.id_num

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
            self.main_multi_shape = MultiShape.create_from_xml_element(shape_element, MultiShapeTimeLine)
            self.main_multi_shape.build_locked_to()
        self.read_linked_clone_element(root)

        for guide_element in root.findall(Guide.TAG_NAME):
            guide = Guide.create_from_xml_element(guide_element)
            if guide:
                self.guides.append(guide)

        self.main_multi_shape.perform_post_create_from_xml()

    def save(self, filename=None):
        result = False
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
            result = True
        except TypeError as e:
            if backup_file:
                os.rename(backup_file, filename)
                backup_file = None

        if backup_file:
            os.remove(backup_file)
        return True

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

    @staticmethod
    def get_icon_pixbuf(icon_name, scale=None, size=20):
        filename = os.path.join(Settings.ICONS_FOLDER, icon_name + ".xml")
        doc = Document(filename=filename)
        if scale:
            doc.main_multi_shape.scale_border_width(scale)
        width = height = size
        pixbuf = doc.get_pixbuf(width=width, height=height, bg_color=False)
        return pixbuf

    @staticmethod
    def create_image(icon_name, scale=None, size=20):
        pixbuf = Document.get_icon_pixbuf(icon_name, scale=scale, size=size)
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

    @staticmethod
    def make_movie(doc_movie, speed=1, sleep=0, fps=24, wh=None,
                   ffmpeg_params=FFMPEG_PARAMS, bitrate=BIT_RATE,
                   codec=CODEC, audio=True, dry=False):

        speed = float(speed)
        doc_movie.load_doc()
        doc_movie.calculate_movie_duration(speed)
        frame_maker = FrameMaker(doc_movie, wh=wh, speed=speed, sleep=sleep)
        video_clip = movie_editor.VideoClip(
                frame_maker.make_frame,
                duration=doc_movie.movie_duration
        )

        if isinstance(ffmpeg_params, str):
            ffmpeg_params = ffmpeg_params.split(" ")
        if audio:
            audio_clips = None
            audio_clips = doc_movie.get_audio_clips(speed=speed)
            if audio_clips:
                audio_clip = movie_editor.CompositeAudioClip(audio_clips)
                video_clip = video_clip.set_audio(audio_clip)
        if dry:
            return
        start_time = time.time()
        video_clip.write_videofile(
            doc_movie.dest_filename, fps=fps,
            codec=codec, preset="superslow",
            ffmpeg_params=ffmpeg_params,
            bitrate=bitrate)
        elapsed_time = time.time()-start_time
        doc_movie.unload_doc()
        ret = "Video {0} is maded in {1:.2f} sec".format(doc_movie.dest_filename, elapsed_time)
        print ret
        return ret

    @staticmethod
    def list2dict(list_items):
        dict_item = dict()
        for i in range(0, len(list_items), 2):
            dict_item[list_items[i]] = list_items[i+1]
        return dict_item

    @staticmethod
    def make_movie_faster(process_count, doc_movie, **kwargs):
        if process_count == 1:
            Document.make_movie(doc_movie, **kwargs)
        else:
            ps_st = time.time()
            segment_count = process_count*2

            duration = doc_movie.end_time-doc_movie.start_time
            duration_steps = duration*1./segment_count
            start_time = doc_movie.start_time
            sub_filenames = []
            args_list = []
            filename_pre, file_extension = os.path.splitext(doc_movie.dest_filename)

            if doc_movie.audio_only:
                doc_movie.load_doc()
                audio_clips = doc_movie.get_audio_clips(kwargs.get("speed", 1))
                audio_clip = movie_editor.CompositeAudioClip(audio_clips)
                audio_clip.write_audiofile(doc_movie.dest_filename)
                print "Audio {0} is made in {1:.2f} sec".format(
                            doc_movie.dest_filename, time.time()-ps_st)
                return

            has_audio = kwargs.get("audio", False)
            kwargs["audio"] = False

            for i in range(segment_count):
                sub_filename = "{0}.{1}{2}".format(filename_pre, i, file_extension)
                sub_filenames.append(sub_filename)
                args = [
                    ("src_filename", doc_movie.src_filename,
                    "dest_filename", sub_filename,
                    "time_line", doc_movie.time_line_name,
                    "start_time", start_time,
                    "end_time", min(start_time+duration_steps, doc_movie.end_time),
                    "camera", doc_movie.camera_name)
                ]
                for key, value in kwargs.items():
                    args.extend([key, value])
                args_list.append(args)
                start_time += duration_steps

            pool = multiprocessing.Pool(processes=process_count)
            result = pool.map_async(make_movie_processed, args_list)
            pool.close()
            result.get(timeout=60*60*24)

            clips = []
            for sub_filename in sub_filenames:
                clips.append(movie_editor.VideoFileClip(sub_filename))

            final_clip = movie_editor.concatenate_videoclips(clips)
            if has_audio:
                doc_movie.load_doc()
                audio_clips = doc_movie.get_audio_clips(kwargs.get("speed", 1))
                if audio_clips:
                    audio_clip = movie_editor.CompositeAudioClip(audio_clips)
                    final_clip = final_clip.set_audio(audio_clip)
            final_clip.write_videofile(
                doc_movie.dest_filename,
                ffmpeg_params = kwargs.get("ffmpeg_params", Document.FFMPEG_PARAMS).split(" "),
                codec = kwargs.get("codec", Document.CODEC), preset="superslow",
                bitrate = kwargs.get("bitrate", Document.BIT_RATE),
            )

            for sub_filename in sub_filenames:
                os.remove(sub_filename)

            print "Video {0} is made in {1:.2f} sec".format(doc_movie.dest_filename, time.time()-ps_st)
        return True

    @staticmethod
    def load_modules(*items):
        for item in items:
            if type(item) in (list, tuple):
                module_name = item[0]
                module_path = item[1]
            else:
                module_name = os.path.basename(os.path.splitext(item)[0])
                prog = re.compile("[\[\]\*\?\!]+")
                if prog.findall(module_name):
                    directory = os.path.dirname(item)
                    basename = os.path.basename(item)
                    for filename in os.listdir(directory):
                        if not fnmatch.fnmatch(filename, basename):
                            continue
                        filepath = os.path.join(directory, filename)
                        if not os.path.isfile(filepath):
                            continue
                        Document.load_modules(filepath)
                    return
                module_path = item
            doc_module = DocModule(module_name, module_path)

    @classmethod
    def load_and_get_main_multi_shape(cls, filename):
        doc = cls(filename=filename)
        return (doc.width, doc.height), doc.main_multi_shape

def make_movie_processed(args):
    params = Document.list2dict(args[1:])
    params["doc_movie"] = DocMovie(**Document.list2dict(args[0]))
    Document.make_movie(**params)

class DocModule(MultiShapeModule):
    def __init__(self, module_name, module_path):
        super(DocModule, self).__init__(module_name, module_path)

    def load(self):
        if not self.root_multi_shape:
            doc = Document(filename=self.module_path)
            doc.main_multi_shape.translation.assign(0, 0)
            self.root_multi_shape = doc.main_multi_shape

    def unload(self):
        if self.root_multi_shape:
            self.root_multi_shape = None

class DocMovie(object):
    def __init__(self, src_filename, dest_filename, time_line=None,
                       start_time=0, end_time=None, camera=None,
                       audio_only=False,):
        doc = Document(filename=src_filename)

        timelines = doc.main_multi_shape.timelines
        if not timelines:
            raise Exception("No timeline is found in {0}".format(filename))

        if time_line is None:
            if "main" in timelines.keys():
                time_line = "main"
            else:
                time_line = timelines.keys()[0]
        elif time_line not in timelines:
            raise Exception("Timeline [{1}] is not found in {0}".format(
                                        filename, time_line))

        time_line_obj = timelines[time_line]

        if end_time is None:
            end_time = time_line_obj.duration
        if camera:
            if not doc.get_shape_by_name(camera):
                camera = None

        self.src_filename = src_filename
        self.dest_filename = dest_filename

        self.time_line_name = time_line
        self.start_time = start_time
        self.end_time = end_time
        self.camera_name = camera
        self.duration = self.end_time-self.start_time
        self.movie_offset = 0
        self.movie_duration = 0
        self.doc = None
        self.camera = None
        self.time_line = None
        self.audio_only = audio_only

    def set_movie_offset(self, offset):
        self.movie_offset = offset

    def calculate_movie_duration(self, speed):
        self.movie_duration = self.duration/speed

    def load_doc(self):
        if not self.doc:
            self.doc = Document(filename=self.src_filename)
            self.time_line = self.doc.main_multi_shape.timelines[self.time_line_name]
            if self.camera_name:
                self.camera = self.doc.get_shape_by_name(self.camera_name)

    def unload_doc(self):
        if self.doc:
            self.doc = None
            self.camera = None

    def get_audio_clips(self, speed):
        self.load_doc()
        return self.time_line.get_audio_clips(
                    abs_time_offset = self.movie_offset,
                    pre_scale=speed,
                    slice_start_at=self.start_time,
                    slice_end_at=self.end_time)

    @classmethod
    def create_from_params(cls, filename, params):
        time_line=None
        start_time=0
        end_time=None
        camera=None
        audio_only = False
        dest_filename = filename + ".video"
        for i in range(len(params)):
            param = params[i]
            arr = param.split("=")
            if len(arr) == 1:
                continue
            param_name = arr[0]
            param_value = arr[1]
            if param_name == "time_line":
                time_line = param_value
            elif param_name == "start_time":
                start_time = Text.parse_number(param_value, 0)
            elif param_name == "end_time":
                end_time = Text.parse_number(param_value, None)
            elif param_name == "camera":
                camera = param_value
            elif param_name == "output":
                dest_filename = param_value
            elif param_name == "audio_only":
                audio_only = (param_value == "True")
        return cls(src_filename=filename, dest_filename=dest_filename,
                   time_line=time_line, audio_only=audio_only,
                   start_time=start_time, end_time=end_time, camera=camera)

class FrameMaker(object):
    def __init__(self, doc_movie, wh=None, speed=1, bg_color="FFFFFF", sleep=0):
        self.doc_movie = doc_movie
        self.sleep= sleep
        self.speed = float(speed)
        self.bg_color = bg_color

        if wh:
            width, height = wh.split("x")
            self.width = float(width)
            self.height = float(height)
        else:
            doc_movie.load_doc()
            if doc_movie.camera:
                self.width, self.height = doc_movie.camera.width, doc_movie.camera.height
            else:
                self.width, self.height = doc_movie.doc.width, doc_movie.doc.height
            #doc_movie.unload_doc()

        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, int(self.width), int(self.height))
        self.ctx = cairo.Context(self.surface)
        set_default_line_style(self.ctx)
        self.drawing_size = Point(self.width, self.height)

    def make_frame(self, t):
        if self.sleep:
            time.sleep(self.sleep)
        self.doc_movie.time_line.move_to(t*self.speed+self.doc_movie.start_time)

        if self.bg_color:
            self.ctx.rectangle(0, 0, self.width, self.height)
            draw_fill(self.ctx, self.bg_color)
        self.ctx.save()

        camera = self.doc_movie.camera
        multi_shape = self.doc_movie.doc.main_multi_shape
        if camera is None:
            camera = multi_shape.camera

        if camera:
            view_width = camera.width
            view_height = camera.height
        else:
            view_width = self.doc_movie.doc.width
            view_height = self.doc_movie.doc.height

        dw_width = float(self.width)
        dw_height = float(self.height)

        sx, sy = dw_width/view_width, dw_height/view_height
        scale = min(sx, sy)

        view_left = (dw_width-scale*view_width)*.5
        view_top = (dw_height-scale*view_height)*.5

        self.ctx.translate(view_left, view_top)
        self.ctx.scale(scale, scale)

        if camera:
            camera.reverse_pre_draw(self.ctx, root_shape=multi_shape.parent_shape)

        pre_matrix = self.ctx.get_matrix()
        multi_shape.draw(self.ctx, drawing_size=self.drawing_size, fixed_border=True,
            root_shape=multi_shape.parent_shape, pre_matrix=pre_matrix)

        self.ctx.restore()
        return ImageHelper.surface2array(self.surface, reformat=True, rgb_only=True)
