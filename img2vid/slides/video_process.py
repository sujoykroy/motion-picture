import multiprocessing
import threading
import time

from commons import AppConfig
from slides import VideoFrameMaker

class VideoProcess(multiprocessing.Process):
    def __init__(self, video_frame_maker, dest_filename, config):
        super(VideoProcess, self).__init__()
        self.maker_data = video_frame_maker.serialize()
        self.dest_filename = dest_filename
        self.config_filename = config.filepath
        self.elapsed = multiprocessing.Value('f', 0)
        self.video_frame_maker = None
        self.config = None
        self.update_thread = None

    def run(self):
        self.config = AppConfig(self.config_filename)
        self.video_frame_maker = VideoFrameMaker.create_from_data(self.maker_data, self.config)
        self.update_thread = UpdateThread(self)
        self.video_frame_maker.make_video(self.dest_filename, self.config)
        self.update_thread.close()

class UpdateThread(threading.Thread):
    def __init__(self, process):
        super(UpdateThread, self).__init__()
        self.process = process
        self.should_close = False
        self.start()

    def close(self):
        self.should_close = True
        self.join()

    def run(self):
        while not self.should_close:
            self.process.elapsed.value = self.process.video_frame_maker.last_max_t
            time.sleep(1)

class ThreadValue:
    def __init__(self):
        self.value = 0

class VideoThread(threading.Thread):
    def __init__(self, video_maker, dest_filename, config):
        super(VideoThread, self).__init__()
        self.dest_filename = dest_filename
        self.video_frame_maker = video_maker
        self.video_frame_maker.delay = .1
        self.elapsed = ThreadValue()
        self.video_frame_maker.make_frame_callback = self.update_elapsed
        self.config = config
        self.should_close = False

    def update_elapsed(self):
        self.elapsed.value = self.video_frame_maker.last_max_t
        return not self.should_close

    def terminate(self):
        self.should_close = True
        if self.is_alive():
            self.join(timeout=.10)

    def run(self):
        try:
            self.video_frame_maker.make_video(self.dest_filename, self.config)
        except:
            pass