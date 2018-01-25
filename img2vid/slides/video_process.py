import multiprocessing
import threading
import time

from commons import AppConfig
from slides import VideoFrameMaker

class VideoProcess(multiprocessing.Process):
    def __init__(self, maker_data, dest_filename, config_filename):
        super(VideoProcess, self).__init__()
        self.maker_data = maker_data
        self.dest_filename = dest_filename
        self.config_filename = config_filename
        self.elapsed = multiprocessing.Value('f', 0)

    def run(self):
        config = AppConfig(self.config_filename)
        self.video_frame_maker = VideoFrameMaker.create_from_data(self.maker_data, config)
        self.update_thread = UpdateThread(self)
        self.video_frame_maker.make_video(self.dest_filename, config)
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