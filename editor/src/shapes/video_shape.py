from ..commons import *
from rectangle_shape import RectangleShape, Shape
from gi.repository import Gdk, GdkPixbuf, GLib
from gi.repository.GdkPixbuf import Pixbuf
from moviepy.editor import *
import sys
from ..audio_tools import *
from audio_shape import AudioShape

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
        self.use_thread = True
        self.audio_queue = None
        self.audio_active = True

    def copy(self, copy_name=False, deep_copy=False):
        newob = VideoShape(self.anchor_at.copy(), copy_value(self.border_color), self.border_width,
                        copy_value(self.fill_color), self.width, self.height, self.corner_radius)
        self.copy_into(newob, copy_name)
        newob.set_video_path(self.video_path)
        newob.alpha = self.alpha
        return newob

    def get_xml_element(self):
        elm = RectangleShape.get_xml_element(self)
        elm.attrib["video_path"] = self.video_path
        elm.attrib["alpha"] = "{0}".format(self.alpha)
        elm.attrib["duration"] = "{0}".format(self.duration)
        if not self.audio_active:
            elm.attrib["audio_active"] = "0"
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        shape = super(VideoShape, cls).create_from_xml_element(elm)
        shape.set_video_path(elm.attrib.get("video_path", ""))
        shape.alpha = float(elm.attrib.get("alpha", 1.))
        shape.audio_active = bool(int(elm.attrib.get("audio_active", 1)))
        return shape

    def set_video_path(self, video_path):
        self.video_path = video_path
        video_clip = VideoFileClip(self.video_path)
        self.duration =  video_clip.duration
        self.image_pixbuf = None

    def get_duration(self):
        return self.duration

    def get_video_length(self):
        return "{0:.2f} sec".format(self.duration)

    def get_av_filename(self):
        return self.video_path

    def can_draw_time_slice_for(self, prop_name):
        return True if prop_name == "time_pos" else False

    def set_time_pos(self, time_pos, prop_data=None):
        if prop_data and False:
            filename = prop_data.get("av_filename")
            if filename:
                self.set_video_path(filename)
        if time_pos<0:
            return
        if self.video_clip is None:
            self.video_clip = VideoFileClip(self.video_path)
            self.duration = self.video_clip.duration
        if time_pos>self.video_clip.duration:
            time_pos = self.video_clip.duration

        self.time_pos = time_pos

        if self.use_thread:
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
        if not self.use_thread or self.process_thread is None:
            frame = self.video_clip.get_frame(self.time_pos)
            self.image_pixbuf = self.get_pixbuf_from_frame(frame)

        if AudioShape.DONT_PLAY or not self.audio_active:
            return
        audio_thread = AudioJack.get_thread()
        if not audio_thread:
            return
        if self.audio_queue is None:
            self.audio_queue = audio_thread.get_new_audio_queue()

        audio_file = AudioFileCache.get_file(self.video_path)
        start_at = self.time_pos
        end_at = self.time_pos + AudioShape.TIME_STEP
        samples = audio_file.get_samples_in_between(start_at, end_at).copy()
        audio_thread.clear_audio_queue(self.audio_queue)
        try:
            self.audio_queue.put(samples, block=False)
        except Queue.Full as e:
            pass

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

    def draw_image(self, ctx, root_shape=None):
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

    def draw_for_time_slice(self, ctx, prop_name, prop_data, visible_time_span,
                                 time_slice, time_slice_box, pixel_per_second):
        AudioShape.draw_for_time_slice(
            ctx, prop_name, prop_data, visible_time_span,
                 time_slice, time_slice_box, pixel_per_second)

    def cleanup(self):
        RectangleShape.cleanup(self)
        if self.process_thread is not None:
            self.process_thread.should_stop = True
            self.process_thread.join()
            self.process_thread = None
        if self.audio_queue:
            audio_jack = AudioJack.get_thread()
            if audio_jack:
                audio_jack.remove_audio_queue(self.audio_queue)
        self.audio_queue = None
