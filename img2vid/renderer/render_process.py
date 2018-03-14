import multiprocessing
import time
import queue

from ..slides import Project, VideoCache
from ..configs import VideoRenderConfig, TextConfig, ImageConfig
from ..renderer import SlideRenderer
from .render_info import RenderInfo


class ImageRenderProcess(multiprocessing.Process):
    ACTION_SLIDE_IMAGE = "img"
    ACTION_SHUTDOWN = "shhutdown"

    def __init__(self):
        super().__init__()
        self._in_queue = multiprocessing.Queue()
        self._out_queue = multiprocessing.Queue(1)

    def run(self):
        while True:
            action_name = None
            action_data = None
            for _ in range(10):
                try:
                    action = self._in_queue.get(block=False)
                except queue.Empty:
                    break
                action_name = action[0]
                if action_name == self.ACTION_SHUTDOWN:
                    break
                action_data = action[1:]

            if action_name == self.ACTION_SHUTDOWN:
                VideoCache.clear_cache()
                break

            if action_data:
                render_info = self._render_slide(
                    slide=action_data[0],
                    screen_config=action_data[1],
                    extra_config=action_data[2])
                if render_info:
                    try:
                        self._out_queue.put(render_info.get_json(), block=False)
                    except queue.Full:
                        pass
            time.sleep(.1)

    def get_render_info(self):
        try:
            render_info_data = self._out_queue.get(block=False)
        except queue.Empty:
            return None
        return RenderInfo.create_from_json(render_info_data)

    def build_slide(self, slide, screen_config, extra_config):
        self.clear()
        self._in_queue.put((
            self.ACTION_SLIDE_IMAGE,
            slide.get_json(),
            screen_config.get_json(),
            extra_config.get_json()))

    def clear(self):
        while not self._in_queue.empty():
            try:
                self._in_queue.get(block=False)
            except queue.Empty:
                break

        while not self._out_queue.empty():
            try:
                self._out_queue.get(block=False)
            except queue.Empty:
                break

    def shutdown(self):
        self._in_queue.put((self.ACTION_SHUTDOWN,))
        self.join(5)
        self.terminate()

    @staticmethod
    def _render_slide(slide, screen_config, extra_config):
        slide = Project.create_slide_from_json(slide)
        screen_config = VideoRenderConfig.create_from_json(screen_config)

        if extra_config['TYPE_NAME'] == TextConfig.TYPE_NAME:
            extra_config = TextConfig.create_from_json(extra_config)
            return SlideRenderer.build_text_slide(slide, screen_config, extra_config)
        elif extra_config['TYPE_NAME'] == ImageConfig.TYPE_NAME:
            extra_config = ImageConfig.create_from_json(extra_config)
            return SlideRenderer.build_image_slide(slide, screen_config, extra_config)
        return None
