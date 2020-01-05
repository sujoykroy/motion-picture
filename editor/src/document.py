# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import dump as XmlDump
from xml.etree.ElementTree import ElementTree as XmlTree
from xml.etree.ElementTree import Element as XmlElement

from gi.repository import Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
import cairo, os

from . import settings as Settings
from .commons import *
from .shapes import *
from .commons.guides import Guide
from .tasks import TaskManager
from .time_lines import MultiShapeTimeLine
from .time_lines import TimeSlice

from .audio_tools import AudioBlock

import moviepy.editor as movie_editor
import numpy
import time
import fnmatch
import re
import multiprocessing
import sys
from tqdm import tqdm
import moviepy.config
import subprocess
import uuid

class Document(object):
    IdSeed = 0

    def __init__(self, filename=None, width=400., height=300.):
        Settings.Directory.add_new(filename)
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

    def __eq__(self, other):
        return isinstance(other, Document) and other.id_num == self.id_num

    def is_empty(self):
        return not self.filename and self.reundo.is_empty()

    def get_main_multi_shape(self):
        return self.main_multi_shape

    def get_shape_by_name(self, name):
        return self.main_multi_shape.get_interior_shape(name)

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
            print(e)
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
            self.main_multi_shape.build_locked_to(up=-100000)

        for guide_element in root.findall(Guide.TAG_NAME):
            guide = Guide.create_from_xml_element(guide_element)
            if guide:
                self.guides.append(guide)

        self.read_linked_clone_element(root)
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
            tree.write(self.filename, encoding="utf-8", xml_declaration=True)
            result = True
        except TypeError as e:
            print("{0}".format(e))
        except UnicodeDecodeError as e:
            print("{0}".format(e))

        if not result:
            if backup_file:
                os.rename(backup_file, filename)
                backup_file = None
                sys.exit("Unable to save file")

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
                name_text = linked_clone_element.text
                linked_clone_name = name_text.split(".")
                linked_shape = get_shape_at_hierarchy(self.main_multi_shape, linked_clone_name)
                if not linked_shape:
                    continue
                linked_shape.set_linked_to(source_shape)
                linked_shape.copy_data_from_linked(build_lock=True)

    def get_surface(self, width, height, bg_color=None):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        ctx = cairo.Context(surface)
        if bg_color:
            ctx.rectangle(0, 0, width, height)
            draw_fill(ctx, bg_color)
        ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

        shape = self.main_multi_shape
        scale = min(width*1./self.width, height*1./self.height)
        ctx.translate((width-scale*self.width)*.5, (height-scale*self.height)*.5)
        ctx.scale(scale, scale)
        set_default_line_style(ctx)
        shape.draw(ctx, Point(self.width, self.height), self.fixed_border)
        return ctx.get_target()

    def get_pixbuf(self, width, height, bg_color=None):
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

    """
    #make movie is transferred to DocMove
    these fucntions need to be deleted from Document class
    @staticmethod
    def make_movie(doc_movie, sleep=0, fps=24, wh=None,
                   ffmpeg_params="", bitrate="",
                   codec="", audio=True, dry=False):
        doc_movie.load_doc()
        frame_maker = VideoFrameMaker(doc_movie, wh=wh, sleep=sleep)
        video_clip = movie_editor.VideoClip(
                frame_maker.make_frame,
                duration=doc_movie.movie_duration
        )

        if isinstance(ffmpeg_params, str):
            ffmpeg_params = ffmpeg_params.split(" ")
        if audio:
            audio_clip = doc_movie.get_audio_frame_maker()
            video_clip = video_clip.set_audio(audio_clip)
        if dry:
            return
        start_time = time.time()
        if doc_movie.is_gif:
            frame_maker.write_gif(video_clip, fps)
        else:
            video_clip.write_videofile(
                doc_movie.dest_filename, fps=fps,
                codec=codec, preset=Document.PRESET,
                ffmpeg_params=ffmpeg_params,
                bitrate=bitrate)
        elapsed_time = time.time()-start_time
        doc_movie.unload_doc()
        ret = "Video {0} is made in {1:.2f} sec".format(doc_movie.dest_filename, elapsed_time)
        print(ret)
        return ret

    @staticmethod
    def make_movie_faster(process_count, doc_movie, **kwargs):
        if process_count == 1 or doc_movie.dest_filename[-4:] == ".gif" \
                        or kwargs.get("dry", False):
            Document.make_movie(doc_movie, **kwargs)
        else:
            ps_st = time.time()
            segment_count = process_count*2

            duration = doc_movie.end_time-doc_movie.start_time
            duration_steps = duration*1./segment_count
            start_time = doc_movie.start_time
            sub_filenames = []
            clip_durations = []
            args_list = []
            filename_pre, file_extension = os.path.splitext(doc_movie.dest_filename)

            if doc_movie.audio_only:
                doc_movie.load_doc()
                audio_clip = movie_editor.CompositeAudioClip(audio_clips)
                audio_clip.write_audiofile(doc_movie.dest_filename)
                print("Audio {0} is made in {1:.2f} sec".format(
                            doc_movie.dest_filename, time.time()-ps_st))
                return

            has_audio = kwargs.get("audio", False)
            kwargs["audio"] = False

            for i in range(segment_count):
                sub_filename = "{0}.{1}{2}".format(filename_pre, i, file_extension)
                sub_filenames.append(sub_filename)
                end_time = min(start_time+duration_steps, doc_movie.end_time)
                clip_durations.append((end_time-start_time)/doc_movie.speed)
                args = [
                    ("src_filename", doc_movie.src_filename,
                    "dest_filename", sub_filename,
                    "time_line", doc_movie.time_line_name,
                    "start_time", start_time,
                    "end_time", end_time,
                    "camera", doc_movie.camera_name,
                    "speed", doc_movie.speed,
                    "bg_color", doc_movie.bg_color)
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
            for i in xrange(len(sub_filenames)):
                clip=movie_editor.VideoFileClip(sub_filenames[i])
                clip = clip.subclip(0, clip_durations[i])#to eliminated extra frames at end
                clips.append(clip)

            final_clip = movie_editor.concatenate_videoclips(clips)
            if has_audio:
                doc_movie.load_doc()
                audio_clip = doc_movie.get_audio_frame_maker()
                final_clip = final_clip.set_audio(audio_clip)

            final_clip.write_videofile(
                doc_movie.dest_filename,
                ffmpeg_params = kwargs.get("ffmpeg_params", Document.FFMPEG_PARAMS).split(" "),
                codec = kwargs.get("codec", Document.CODEC), preset=Document.PRESET,
                bitrate = kwargs.get("bitrate", Document.BIT_RATE),
            )

            for sub_filename in sub_filenames:
                os.remove(sub_filename)

            print("Video {0} is made in {1:.2f} sec".format(doc_movie.dest_filename, time.time()-ps_st))
        return True
    """

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
            doc_module = DocModule.create(module_name, module_path)

    LoadedFiles = dict()

    @classmethod
    def load_and_get_main_multi_shape(cls, filename, folder=None):
        if folder is not None:
            filename = os.path.join(folder, filename)
        if filename in Document.LoadedFiles:
            doc = Document.LoadedFiles[filename]
        else:
            doc = cls(filename=filename)
            Document.LoadedFiles[filename] = doc
        return (doc.width, doc.height), doc.main_multi_shape

    @classmethod
    def unload_file(cls, filename):
        if filename not in Document.LoadedFiles:
            return
        doc = Document.LoadedFiles[filename]
        del Document.LoadedFiles[filename]
        doc.main_multi_shape.cleanup()
        del doc

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

def make_movie_processed(args):
    params = dict()
    for i in range(0, len(args), 2):
        params[args[i]] = args[i+1]
    doc_movie = DocMovie(**params)
    doc_movie.make()

class DocMovie(object):
    FFMPEG_PARAMS = "-quality good -qmin 10 -qmax 42"
    BIT_RATE = "640k"
    CODEC = "libvpx"
    PRESET = "superslow"

    def __init__(self, src_filename, dest_filename,
                       time_line=None, start_time=0, end_time=None,
                       camera=None, bg_color=None,
                       audio_only=False, audio=True, process_count=1,
                       fps=24, resolution="1280x720", speed=1, dry=False,
                       ffmpeg_params=FFMPEG_PARAMS, bit_rate=BIT_RATE, codec=CODEC,
                       gif_params=""):

        width, height = resolution.split("x")
        self.width = float(width)
        self.height = float(height)
        self.gif_params = gif_params

        if (src_filename[-3:] == ".py"):
            folder=os.path.dirname(dest_filename)
            temp_filename = "temp_{0}.mp.xml".format(uuid.uuid4())
            doc_filename = os.path.join(folder, temp_filename)
            doc = Document(width=self.width, height=self.height)
            custom_shape = CustomShape(
                   anchor_at=Point(doc.width*.5, doc.height*.5),
                   border_color=None,
                   border_width=0, fill_color=None,
                   width=doc.width, height=doc.height, corner_radius=0)
            custom_shape.set_code_path(src_filename, init=True)
            doc.main_multi_shape.shapes.add(custom_shape)
            new_time_line = doc.main_multi_shape.get_new_timeline(MultiShapeTimeLine)
            if end_time is None:
                end_time = 0
            time_slice = TimeSlice(0, 1, duration=end_time)
            new_time_line.add_shape_prop_time_slice(custom_shape, "progress", time_slice)
            doc.save(doc_filename)
            self.script_filename = src_filename
            src_filename = doc_filename
            time_line = new_time_line.name
        else:
            self.script_filename = None

        self.is_gif = (dest_filename[-4:] == ".gif")
        self.is_png = (dest_filename[-4:] == ".png")

        doc = Document(filename=src_filename)
        timelines = doc.main_multi_shape.timelines

        if not timelines and not self.is_png:
            raise Exception("No timeline is found in {0}".format(src_filename))

        if timelines:
            if time_line is None:
                if not self.is_png:
                    if u"main" in timelines:
                        time_line = u"main"
                    else:
                        time_line = timelines.keys()[0]
            elif time_line not in timelines:
                raise Exception("Timeline [{1}] is not found in {0}".format(
                                            src_filename, time_line))
        if time_line:
            time_line_obj = timelines[time_line]
            if end_time is None:
                end_time = time_line_obj.duration
        if camera:
            if isinstance(camera, str):
                camera = camera.decode("utf-8")
            if not doc.get_shape_by_name(camera):
                camera = None

        self.src_filename = src_filename
        self.dest_filename = dest_filename
        self.time_line_name = time_line
        self.start_time = start_time
        self.end_time = end_time
        self.camera_name = camera
        self.speed = speed
        self.bg_color = bg_color
        self.fps = fps
        self.audio = audio
        self.process_count = process_count
        self.ffmpeg_params = ffmpeg_params
        self.bit_rate = bit_rate
        self.codec = codec
        self.dry = dry
        self.resolution = resolution

        self.duration = self.end_time-self.start_time
        self.doc = None
        self.camera = None
        self.time_line = None
        self.audio_only = audio_only
        self.movie_duration = self.duration/self.speed

    def load_doc(self):
        if not self.doc:
            self.doc = Document(filename=self.src_filename)
            if self.time_line_name:
                self.time_line = self.doc.main_multi_shape.timelines[self.time_line_name]
            if self.camera_name:
                self.camera = self.doc.get_shape_by_name(self.camera_name)

    def unload_doc(self):
        if self.doc:
            self.doc = None
            self.camera = None

    def make(self):
        ps_st = time.time()

        #if self.is_png:
        #    self.load_doc()
        #    if self.time_line:
        #        self.time_line.move_to(self.start_time)
        #    pixbuf = self.doc.get_pixbuf(self.width, self.height, bg_color=self.bg_color)
        #    pixbuf.savev(self.dest_filename, "png", [], [])
        #    self.unload_doc()
        if self.audio_only:
            audio_clip = AudioFrameMaker(self)
            audio_clip.write_audiofile(self.dest_filename)
        elif self.process_count == 1 or self.is_gif or self.dry or self.is_png:
            self.load_doc()
            frame_maker = VideoFrameMaker(self, width=self.width, height=self.height)
            video_clip = movie_editor.VideoClip(frame_maker.make_frame, duration=self.movie_duration)

            if self.audio:
                audio_clip = AudioFrameMaker(self)
                video_clip = video_clip.set_audio(audio_clip)

            if self.dry:
                return
            if self.is_gif:
                frame_maker.write_gif(video_clip, self.fps)
            elif self.is_png:
                frame_maker.write_png(video_clip, self.start_time, self.dest_filename)
            else:
                video_clip.write_videofile(
                    self.dest_filename,
                    fps = self.fps,
                    codec = self.codec,
                    preset=self.PRESET,
                    ffmpeg_params = self.ffmpeg_params.split(" "),
                    bitrate = self.bit_rate)
            self.unload_doc()
        else:
            segment_count = self.process_count*2

            duration = self.end_time-self.start_time
            duration_steps = duration*1./segment_count
            start_time = self.start_time
            sub_filenames = []
            clip_durations = []
            args_list = []
            filename_pre, file_extension = os.path.splitext(self.dest_filename)

            if self.audio_only:
                self.load_doc()
                audio_clip = movie_editor.CompositeAudioClip(audio_clips)
                audio_clip.write_audiofile(self.dest_filename)
                print("Audio {0} is made in {1:.2f} sec".format(
                            self.dest_filename, time.time()-ps_st))
                return

            for i in range(segment_count):
                sub_filename = "{0}.{1}{2}".format(filename_pre, i, file_extension)
                sub_filenames.append(sub_filename)
                end_time = min(start_time+duration_steps, self.end_time)
                clip_durations.append((end_time-start_time)*1.0/self.speed)
                args = [
                        "src_filename", self.src_filename,
                        "dest_filename", sub_filename,
                        "time_line", self.time_line_name,
                        "start_time", start_time, "end_time", end_time,
                        "camera", self.camera_name, "bg_color", self.bg_color,
                        "audio_only", self.audio_only, "audio", self.audio,
                        "process_count", 1,
                        "fps", self.fps,
                        "resolution", self.resolution, "speed", self.speed,
                        "ffmpeg_params", self.ffmpeg_params,
                        "bit_rate", self.bit_rate, "codec", self.codec
                       ]
                args_list.append(args)
                start_time += duration_steps

            pool = multiprocessing.Pool(processes=self.process_count)
            result = pool.map_async(make_movie_processed, args_list)
            pool.close()
            result.get(timeout=60*60*24)
            if self.dry:
                return
            clips = []
            for i in xrange(len(sub_filenames)):
                clip=movie_editor.VideoFileClip(sub_filenames[i])
                clip = clip.subclip(0, clip_durations[i])#to eliminated extra frames at end
                clips.append(clip)

            final_clip = movie_editor.concatenate_videoclips(clips)
            if self.audio:
                self.load_doc()
                audio_clip = AudioFrameMaker(self)
                final_clip = final_clip.set_audio(audio_clip)

            final_clip.write_videofile(
                self.dest_filename,
                ffmpeg_params = self.ffmpeg_params.split(" "),
                codec = self.codec, preset=self.PRESET,
                bitrate = self.bit_rate
            )

            for sub_filename in sub_filenames:
                os.remove(sub_filename)

        print("Making of {0} is done in {1:.2f} sec".format(self.dest_filename, time.time()-ps_st))
        if self.script_filename:
            os.remove(self.src_filename)

class AudioFrameMaker(movie_editor.AudioClip):
    def __init__(self, doc_movie):
        self.doc_movie = doc_movie
        self.doc_movie.load_doc()
        self.time_line = self.doc_movie.time_line
        self.nchannels = AudioBlock.ChannelCount
        movie_editor.AudioClip.__init__(self, make_frame=None, duration=self.doc_movie.duration)

    def make_frame(self, t):
        t = t*self.doc_movie.speed + self.doc_movie.start_time
        samples = self.time_line.get_samples_at(t, read_doc_shape=True)
        if not isinstance(t, numpy.ndarray):
            t = numpy.array([t])
        if samples is None:
            samples = numpy.zeros((len(t), AudioBlock.ChannelCount), dtype="float")
        elif samples.shape[0]<len(t):
            blank = numpy.zeros(((len(t)-samples.shape[0]), AudioBlock.ChannelCount), dtype="float")
            samples = numpy.append(samples, blank, axis=0)
        return samples

class VideoFrameMaker(object):
    def __init__(self, doc_movie, width=None, height=None, sleep=0):
        self.doc_movie = doc_movie
        self.sleep= sleep

        self.bg_color = self.doc_movie.bg_color
        if not self.bg_color:
            if self.doc_movie.is_gif:
                self.bg_color = "FFFFFF00"
            else:
                self.bg_color = "FFFFFFFF"

        if width is not None and height is not None:
            self.width = float(width)
            self.height = float(height)
        else:
            doc_movie.load_doc()
            if doc_movie.camera:
                self.width, self.height = doc_movie.camera.width, doc_movie.camera.height
            else:
                self.width, self.height = doc_movie.doc.width, doc_movie.doc.height
            #doc_movie.unload_doc()

        if self.doc_movie.is_gif and False:
            self.surface = None
        else:
            self.create_surface()
        self.drawing_size = Point(self.width, self.height)

    def create_surface(self):
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, int(self.width), int(self.height))
        self.ctx = cairo.Context(self.surface)
        set_default_line_style(self.ctx)

    def make_frame(self, t):
        if self.sleep:
            time.sleep(self.sleep)
        self.doc_movie.time_line.move_to(t*self.doc_movie.speed+self.doc_movie.start_time)

        if self.doc_movie.is_gif:
            self.create_surface()
            if self.surface:
                prev_surface_array = ImageHelper.surface2array(
                    self.surface, reformat=True, rgb_only=True)
            else:
                prev_surface_array = None

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
            exclude_camera_list = [camera]
        else:
            exclude_camera_list = []

        pre_matrix = self.ctx.get_matrix()
        multi_shape.draw(self.ctx, drawing_size=self.drawing_size, fixed_border=True,
            no_camera=False, exclude_camera_list=exclude_camera_list,
            root_shape=multi_shape.parent_shape, pre_matrix=pre_matrix)


        self.ctx.restore()
        return ImageHelper.surface2array(self.surface, reformat=True, rgb_only=True)

    def write_png(self, clip, t, filename):
        self.make_frame(t)
        pixbuf= Gdk.pixbuf_get_from_surface(
            self.surface, 0, 0, self.surface.get_width(), self.surface.get_height())
        pixbuf.savev(filename, "png", [], [])

    def write_gif(self, clip, fps=None, program= 'ImageMagick', opt="OptimizeTransparency"):
        filename = self.doc_movie.dest_filename
        file_root, ext = os.path.splitext(filename)
        tt = numpy.arange(0, clip.duration, 1.0/fps)
        tempfiles = []

        print("Building file {0}".format(filename))
        print("Generating GIF frames...")

        total = int(clip.duration*fps)+1
        for i, t in tqdm(enumerate(tt), total=total):
            temp_filename = "{0}_GIFTEMP{1:04d}.png".format(file_root, i+1)
            tempfiles.append(temp_filename)
            clip.make_frame(t)
            self.surface.write_to_png(temp_filename)

        delay = int(100.0/fps)
        fuzz=1
        verbose=True
        loop=0
        dispose=True
        colors=None
        if self.doc_movie.gif_params:
            gif_params = self.doc_movie.gif_params.split(" ")
        else:
            gif_params = []
        if program == "ImageMagick":
            print("Optimizing GIF with ImageMagick... ")
            cmd = [moviepy.config.get_setting("IMAGEMAGICK_BINARY"),
                  '-delay' , '%d'%delay,
                  "-dispose" ,"%d"%(2 if dispose else 1),
                  "-loop" , "%d"%loop,
                  "%s_GIFTEMP*.png"%file_root,
                  "-coalesce",
                  "-layers", "%s"%opt,
                  "-fuzz", "%02d"%fuzz + "%",
                  ]+(["-colors", "%d"%colors] if colors is not None else [])+\
                  gif_params + [filename]

        elif program == "ffmpeg":

            cmd = [moviepy.config.get_setting("FFMPEG_BINARY"), '-y',
                   '-f', 'image2', '-r',str(fps),
                   '-i', filename+'_GIFTEMP%04d.png',
                   '-r',str(fps),
                   filename]

        try:
            subprocess.call(cmd)
            print("%s is ready."%filename)

        except (IOError,OSError) as err:
            error = ("Creation of %s failed because "
              "of the following error:\n\n%s.\n\n."%(filename, str(err)))
            if program == "ImageMagick":
                error = error + ("This error can be due to the fact that "
                    "ImageMagick is not installed on your computer, or "
                    "(for Windows users) that you didn't specify the "
                    "path to the ImageMagick binary in file conf.py." )

            raise IOError(error)
        for f in tempfiles:
            os.remove(f)
