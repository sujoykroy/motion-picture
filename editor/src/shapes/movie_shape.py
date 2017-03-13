from ..commons import *
from rectangle_shape import RectangleShape, Shape
from gi.repository import Gdk, GdkPixbuf, Gio
from gi.repository.GdkPixbuf import Pixbuf
from moviepy.editor import *
import sys

import threading, time, Queue

class MovieProcessThread(threading.Thread):
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

class MovieShape(RectangleShape):
    TYPE_NAME = "Movie"

    def __init__(self, anchor_at, border_color, border_width, fill_color, width, height, corner_radius):
        RectangleShape.__init__(self, anchor_at, border_color, border_width,
                                fill_color, width, height, corner_radius)
        self.movie_path = None
        self.image_pixbuf = None
        self.alpha = 1.
        self.time_pos = 0.
        self.movie_clip = None
        self.process_thread = None

    def copy(self, copy_name=False, deep_copy=False):
        newob = MovieShape(self.anchor_at.copy(), self.border_color.copy(), self.border_width,
                        self.fill_color.copy(), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_movie_path(self.movie_path)
        newob.alpha = self.alpha
        return newob

    def get_xml_element(self):
        elm = MovieShape.get_xml_element(self)
        elm.attrib["movie_path"] = self.movie_path
        elm.attrib["alpha"] = "{0}".format(self.alpha)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        arr = Shape.get_params_array_from_xml_element(elm)
        arr.append(float(elm.attrib.get("corner_radius", 0)))
        shape = cls(*arr)
        shape.assign_params_from_xml_element(elm)
        shape.set_movie_path(elm.attrib.get("movie_path", ""))
        shape.alpha = float(elm.attrib.get("alpha", 1.))
        return shape

    def set_movie_path(self, movie_path):
        self.movie_path = movie_path
        self.movie_clip = VideoFileClip(self.movie_path)
        self.image_pixbuf = None
        self.set_time_pos(0)

    def set_time_pos(self, time_pos):
        self.time_pos = time_pos
        if self.movie_clip is None:
            return
        if time_pos>self.movie_clip.duration:
            time_pos = self.movie_clip.duration
        if time_pos>0:
            if self.process_thread is None:
                self.frame_queue = Queue.Queue(1)
                self.time_queue = Queue.Queue(1)
                self.process_thread = MovieProcessThread(
                    self.movie_clip, self.frame_queue, self.time_queue)
                self.process_thread.start()


        if self.process_thread is not None:
            try:
                self.time_queue.put(time_pos, block=False)
            except Queue.Full as e:
                pass
        else:
            frame = self.movie_clip.get_frame(self.time_pos)
            height, width, channels = frame.shape
            rowstride = width*channels
            image_data = frame.tobytes()
            self.image_pixbuf = Pixbuf.new_from_data(
                image_data, 0, False, 8, width, height, rowstride, None, None).copy()

    def draw_image(self, ctx):
        if self.process_thread:
            try:
                frame = self.frame_queue.get(block=False)
            except Queue.Empty as e:
                frame = None
            if frame is not None:
                height, width, channels =frame.shape
                rowstride = width*channels
                image_data = frame.tobytes()
                self.image_pixbuf = Pixbuf.new_from_data(
                    image_data, 0, False, 8, width, height, rowstride, None, None).copy()

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

