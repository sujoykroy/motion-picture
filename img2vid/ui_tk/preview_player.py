import tkinter as tk
import PIL.ImageTk

from ..renderer import VideoThread
from ..renderer import ImageRenderer

from .dialog import Dialog
from .frame import Frame
from .progress_bar import ProgressBar
from .schedule_task import ScheduleTask

from .utils import UtilsTk

class PreviewPlayer(Frame):
    def __init__(self, master, app_config, video_renderer):
        self.top = tk.Toplevel(master)
        self.top.title("Preview")
        self.top.protocol("WM_DELETE_WINDOW", self.close)

        super().__init__(
            master=self.top,
            app_config=app_config,
            event_names=["close"])
        self.base.pack(expand=1, fill=tk.BOTH)

        self._fps = 10
        self._video_filepath = None
        self._video_renderer = video_renderer
        self._video_process = None

        self.base.columnconfigure(1, weight=1)
        self.base.rowconfigure(1, weight=1)

        self.widgets.top_packer = tk.Frame(
            self.base, relief=tk.GROOVE, borderwidth=1)
        self.widgets.top_packer.grid(
            row=0, column=0, columnspan=2, sticky=tk.W+tk.E)

        self.widgets.close_button = tk.Button(
            self.widgets.top_packer, text="Close", command=self.close)
        self.widgets.close_button.pack(side=tk.RIGHT)

        self.widgets.render_button = tk.Button(
            self.widgets.top_packer, text="Render", command=self._on_render)
        self.widgets.render_button.pack(side=tk.LEFT)

        self.widgets.canvas = tk.Canvas(
            self.base,
            highlightbackground=self.app_config.editor_back_color)
        self.widgets.canvas.grid(
            row=1, column=0, columnspan=2, sticky=tk.N+tk.W+tk.E+tk.S)

        self.widgets.play_button = tk.Button(
            self.base, text="Play", command=self._on_playpause)
        self.widgets.play_button.paused = True
        self.widgets.play_button.grid(row=2, column=0, sticky=tk.S)

        self.widgets.slider = tk.Scale(
            self.base,
            from_=0, to=self._video_renderer.duration,
            orient=tk.HORIZONTAL,
            resolution=1/(self._video_renderer.duration*self._fps),
            command=self._on_slider_move)
        self.widgets.slider.grid(row=2, column=1, sticky=tk.N+tk.S+tk.W+tk.E)

        self.widgets.render_bar = ProgressBar(
            self.base, fill="#00FF00", height=25)
        self.widgets.render_bar.grid(
            row=3, column=0, columnspan=2, sticky=tk.S+tk.W+tk.E)

        self.widgets.canvas.image = None

        self._play_forward_task = ScheduleTask(
            master=self.base,
            period=int(1000/self._fps),
            task=self._move_slider_forward)

        self._canvas_update_task = ScheduleTask(
            master=self.base,
            period=self._play_forward_task.period*5,
            task=self._update_canvas)

        self.widgets.canvas.bind("<Configure>", self._update_canvas)
        UtilsTk.show_widget_at_center(self.top)

    def _on_slider_move(self, _):
        self._canvas_update_task.start()

    def _move_slider_forward(self):
        self.widgets.slider.set(self.widgets.slider.get()+1/self._fps)
        return not self.widgets.play_button.paused and \
            self.widgets.slider.get() < self._video_renderer.duration

    def _update_canvas(self, _=None):
        if self._video_process:
            video_error = self._video_process.get_error()
            if video_error:
                Dialog.show_error("Error in Rendering", str(self._video_process.error))
                self._video_process.clear_error()
            if not self._video_process.is_alive():
                self._video_process = None
                self.widgets.play_button["state"] = tk.NORMAL
                self.widgets.render_button["state"] = tk.NORMAL
                if not video_error:
                    Dialog.show_info(
                        "Complete",
                        "Video is rendered successfully at {}".format(self._video_filepath))
            else:
                self.widgets.slider.set(self._video_process.elapsed)
                self.widgets.render_bar.set_progress(
                    self._video_process.elapsed/self._video_renderer.duration)

        canvas = self.widgets.canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if not canvas_width or not canvas_height:
            return

        elapsed = self.widgets.slider.get()
        image = self._video_renderer.get_image_at(elapsed)
        image = ImageRenderer.fit_inside(
            image, canvas_width, canvas_height)

        canvas.image_tk = PIL.ImageTk.PhotoImage(image=image)
        if not canvas.image:
            canvas.image = canvas.create_image(
                canvas_width*0.5, canvas_height*0.5,
                image=canvas.image_tk, anchor=tk.CENTER)
        else:
            canvas.coords(canvas.image, canvas_width*0.5, canvas_height*0.5)
            canvas.itemconfig(canvas.image, image=canvas.image_tk)

        return self._video_process is not None

    def _set_play_state(self, play):
        if play:
            self._play_forward_task.start()
            self.widgets.play_button.paused = False
            self.widgets.play_button["text"] = "Pause"
        else:
            self._play_forward_task.stop()
            self.widgets.play_button.paused = True
            self.widgets.play_button["text"] = "Play"

    def _on_render(self):
        if self._video_process and self._video_process.is_alive():
            return
        video_filepath = Dialog.ask_for_new_video_file(
            self.app_config.video_types,
            self.app_config.video_render.video_ext)
        if video_filepath:
            self._video_filepath = video_filepath
            self.widgets.render_bar.set_text(video_filepath)

            self._set_play_state(False)
            self.widgets.play_button["state"] = tk.DISABLED
            self.widgets.render_button["state"] = tk.DISABLED

            self._video_process = VideoThread(self._video_renderer, video_filepath)
            self._video_process.start()
            self._canvas_update_task.start()

    def _on_playpause(self):
        if self.widgets.play_button.paused:
            self._set_play_state(play=True)
        else:
            self._set_play_state(play=False)

    def close(self):
        if self._video_process:
            self._video_process.terminate()
        self._video_process = None
        self._play_forward_task.stop()
        self._canvas_update_task.stop()
        self.top.destroy()
        self.events.close.fire()
