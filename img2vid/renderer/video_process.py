import threading

class VideoThread(threading.Thread):
    def __init__(self, video_renderer, dest_filename):
        super(VideoThread, self).__init__()
        self.dest_filename = dest_filename
        self.elapsed = 0

        self._video_renderer = video_renderer
        self._video_renderer.set_frame_callback(self._update_elapsed)

        self.error = None
        self.should_close = False

    def get_error(self):
        return self.error

    def clear_error(self):
        self.error = None

    def terminate(self):
        self.should_close = True
        if self.is_alive():
            self.join(timeout=.10)

    def run(self):
        try:
            self._video_renderer.make_video(self.dest_filename)
        except Exception as error:
            self.error = error

    def _update_elapsed(self):
        self.elapsed = self._video_renderer.last_frame_time
        return not self.should_close
