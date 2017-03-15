from ..commons import *
from rectangle_shape import RectangleShape, Shape
from gi.repository import Gdk, GdkPixbuf, GLib
from gi.repository.GdkPixbuf import Pixbuf
from moviepy.editor import *
import sys

import threading, time, Queue

class VideoProcessThread(threading.Thread):
    def __init__(self, clip, frame_queue, time_queue):
        threading.Thread.__init__(self)
        self.frame_queue = frame_queue
        self.time_queue = time_queue
        self.clip = clip
        self.should_stop = False
        self.period = .1

    def run(self):
        while not self.should_stop:
            startTime = time.time()
            try:
                time_pos = self.time_queue.get(block=False)
            except Queue.Empty as e:
                time_pos = -1
            if time_pos>=0:
                frame = self.clip.get_frame(time_pos)
                try:
                    self.frame_queue.put(frame, block=False)
                except Queue.Full as e:
                    pass
            elapsedTime = time.time() - startTime
            diffTime = self.period - elapsedTime
            if diffTime>0:
                time.sleep(diffTime)

class VideoShape(RectangleShape):
    TYPE_NAME = "Video"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        RectangleShape.__init__(self, anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        self.video_path = None
        self.image_pixbuf = None
        self.alpha = 1.
        self.time_pos = 0.
        self.video_clip = None
        self.duration = 0
        self.process_thread = None

    def copy(self, copy_name=False, deep_copy=False):
        newob = VideoShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_video_path(self.video_path)
        newob.alpha = self.alpha
        return newob

    def get_xml_element(self):
        elm = RectangleShape.get_xml_element(self)
        elm.attrib["video_path"] = self.video_path
        elm.attrib["alpha"] = "{0}".format(self.alpha)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(VideoShape, cls).create_from_xml_element(elm)
        shape.set_video_path(elm.attrib.get("video_path", ""))
        shape.alpha = float(elm.attrib.get("alpha", 1.))
        return shape

    def set_video_path(self, video_path):
        self.video_path = video_path
        video_clip = VideoFileClip(self.video_path)
        self.duration =  video_clip.duration
        self.image_pixbuf = None

    def set_time_pos(self, time_pos):
        if time_pos<0:
            return
        if self.video_clip is None:
            self.video_clip = VideoFileClip(self.video_path)
        if time_pos>self.video_clip.duration:
            time_pos = self.video_clip.duration
        if time_pos>0:
            if self.process_thread is None:
                self.frame_queue = Queue.Queue(1)
                self.time_queue = Queue.Queue(1)
                self.process_thread = VideoProcessThread(
                    self.video_clip, self.frame_queue, self.time_queue)
                self.process_thread.start()

        if self.process_thread is not None:
            try:
                self.time_queue.put(time_pos, block=False)
            except Queue.Full as e:
                pass
        else:
            frame = self.video_clip.get_frame(self.time_pos)
            self.image_pixbuf = self.get_pixbuf_from_frame(frame)

    @staticmethod
    def get_pixbuf_from_frame(frame):
        height, width, channels = frame.shape
        #rowstride = width*channels
        header = b"P6 %d %d 255\n" % (width, height)

        ploader = GdkPixbuf.PixbufLoader.new_with_type("pnm")
        ploader.write(header)
        ploader.write(bytearray(frame.tobytes()))
        ploader.close()
        pixbuf = ploader.get_pixbuf()
        return pixbuf

    def draw_image(self, ctx):
        if self.process_thread:
            try:
                frame = self.frame_queue.get(block=False)
            except Queue.Empty as e:
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


    def cleanup(self):
        RectangleShape.cleanup(self)
        if self.process_thread is not None:
            self.process_thread.should_stop = True
            self.process_thread.join()
            self.process_thread = None

