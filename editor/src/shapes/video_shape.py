from ..commons import *
from .rectangle_shape import RectangleShape, Shape
from gi.repository import Gdk, GdkPixbuf, GLib
from gi.repository.GdkPixbuf import Pixbuf
from moviepy.editor import *
import sys
from .av_base import AVBase
import threading, time
import queue
from .. import settings as Settings

class VideoProcessThread(threading.Thread):
    def __init__(self, clip, frame_queue, time_queue):
        threading.Thread.__init__(self)
        self.frame_queue = frame_queue
        self.time_queue = time_queue
        self.clip = clip
        self.should_stop = False
        self.period = .1
        self.lock = threading.RLock()

    def set_video_clip(self, video_clip):
        self.lock.acquire()
        self.clip = video_clip
        self.lock.release()

    def run(self):
        while not self.should_stop:
            startTime = time.time()
            try:
                time_pos = self.time_queue.get(block=False)
                self.time_queue.task_done()
            except queue.Empty as e:
                time_pos = -1
            if time_pos>=0:
                self.lock.acquire()
                frame = self.clip.reader.get_frame(time_pos)
                self.lock.release()
                try:
                    self.frame_queue.put(frame, block=False)
                except queue.Full as e:
                    pass
            elapsedTime = time.time() - startTime
            diffTime = self.period - elapsedTime
            if diffTime>0:
                time.sleep(diffTime)

class VideoShape(RectangleShape, AVBase):
    TYPE_NAME = "Video"
    USE_IMAGE_THREAD = False

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        RectangleShape.__init__(self, anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        AVBase.__init__(self)
        self.image_pixbuf = None
        self.alpha = 1.

        self.video_clip = None
        self.duration = 0

        self.image_process_thread = None
        self.use_thread = True

    def copy(self, copy_name=False, deep_copy=False):
        newob = VideoShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                        copy_value(self.fill_color), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_av_filename(self.av_filename, recalculate=False)
        newob.duration = self.duration
        newob.alpha = self.alpha
        return newob

    def get_xml_element(self):
        elm = super(VideoShape, self).get_xml_element()
        elm.attrib["video_path"] = self.av_filename
        elm.attrib["alpha"] = "{0}".format(self.alpha)
        elm.attrib["duration"] = "{0}".format(self.duration)
        if not self.audio_active:
            elm.attrib["audio_active"] = "0"
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(VideoShape, cls).create_from_xml_element(elm)
        shape.set_av_filename(elm.attrib.get("video_path", ""))
        shape.alpha = float(elm.attrib.get("alpha", 1.))
        shape.audio_active = bool(int(elm.attrib.get("audio_active", 1)))
        return shape

    def set_av_filename(self, av_filename, recalculate=True):
        if av_filename != "//":
            av_filename = Settings.Directory.get_full_path(av_filename)
        if av_filename == "//":
            self.duration = 0
            self.video_clip = None
            self.image_pixbuf = None
        elif av_filename and av_filename != self.av_filename and recalculate:
            video_clip = VideoFileClip(av_filename)#memory leak area :-)
            self.duration =  video_clip.duration
            self.video_clip = None
            self.image_pixbuf = None

        AVBase.set_av_filename(self, av_filename)

    def get_video_length(self):
        return "{0:.2f} sec".format(self.duration)

    def get_video_path(self):
        return self.av_filename

    def set_video_path(self, filename):
        self.set_av_filename(filename)

    def set_prop_value(self, prop_name, prop_value, prop_data=None):
        if prop_name == "time_pos":
            self.set_time_pos(prop_value, prop_data)
        else:
            super(VideoShape, self).set_prop_value(prop_name, prop_value, prop_data)

    def set_time_pos(self, time_pos, prop_data=None):
        if prop_data:
            av_filename = prop_data.get("video_path")
            self.set_av_filename(av_filename)
        if self.av_filename == "//":
            return
        AVBase.set_time_pos(self, time_pos, prop_data)

        if self.duration == 0:#it will handle self.av_filename == "//"
            return
        if self.video_clip is None:
            self.video_clip = VideoFileClip(self.av_filename, has_mask=True)
            self.duration = self.video_clip.duration
            if self.image_process_thread:
                self.image_process_thread.set_video_clip(self.video_clip)

        if time_pos>self.video_clip.duration:
            time_pos = self.video_clip.duration

        if self.use_thread and VideoShape.USE_IMAGE_THREAD:
            if self.time_pos>0:
                if self.image_process_thread is None:
                    self.frame_queue = queue.Queue(1)
                    self.time_queue = queue.Queue(1)
                    self.image_process_thread = VideoProcessThread(
                        self.video_clip, self.frame_queue, self.time_queue)
                    self.image_process_thread.start()

            if self.image_process_thread is not None:
                try:
                    self.time_queue.put(self.time_pos, block=False)
                except queue.Full as e:
                    pass
        if not self.use_thread or self.image_process_thread is None:
            frame = self.video_clip.reader.get_frame(self.time_pos)
            self.image_pixbuf = self.get_pixbuf_from_frame(frame)

    def get_pixbuf_from_frame(self, frame):
        height, width, channels = frame.shape
        return GdkPixbuf.Pixbuf.new_from_bytes(
            data=GLib.Bytes(frame.tobytes()),
            colorspace=0,
            has_alpha=True,
            bits_per_sample=8,
            width=width,
            height=height,
            rowstride = width*4)

    def draw_image(self, ctx, root_shape=None):
        if self.image_process_thread:
            try:
                frame = self.frame_queue.get(block=False)
                self.frame_queue.task_done()
            except queue.Empty as e:
                frame = None
            if frame is not None:
                self.image_pixbuf = self.get_pixbuf_from_frame(frame)

        if self.image_pixbuf:
            ctx.save()
            ctx.scale(self.width/float(self.image_pixbuf.get_width()),
                      self.height/float(self.image_pixbuf.get_height()))
            Gdk.cairo_set_source_pixbuf(ctx, self.image_pixbuf, 0, 0)
            if self.alpha<1:
                ctx.paint_with_alpha(self.alpha)
            else:
                ctx.paint()
            ctx.restore()

    def can_draw_time_slice_for(self, prop_name):
        return True if prop_name == "time_pos" else False

    def draw_for_time_slice(self, ctx, prop_name, prop_data, visible_time_span,
                                   time_slice, time_slice_box, pixel_per_second):
        if prop_name != "time_pos":
            return
        filename = prop_data["video_path"] if prop_data else None
        if not filename or filename == "//":
            return
        filename = Settings.Directory.get_full_path(filename)
        AVBase.draw_for_time_slice(
            self, ctx, filename, visible_time_span,
                       time_slice, time_slice_box, pixel_per_second)

    def cleanup(self):
        RectangleShape.cleanup(self)
        if self.image_process_thread is not None:
            self.image_process_thread.should_stop = True
            self.image_process_thread.join()
