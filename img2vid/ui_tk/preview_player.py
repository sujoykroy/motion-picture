import tkinter as tk
from tkinter import filedialog
import wand

from commons import Rectangle
from slides import VideoProcess, VideoThread
from .canvas_image import CanvasImage
from .progress_bar import ProgressBar

class PreviewPlayer:
    def __init__(self, parent, video_frame_maker, config, on_close_callback):
        self.fps = 10
        self.config = config
        self.millisecond_per_frame = 1/self.fps
        self.video_frame_maker = video_frame_maker
        self.video_process = None
        self.on_close_callback = on_close_callback

        top = self.top = tk.Toplevel(parent, relief=tk.RIDGE, borderwidth=1)
        top.protocol("WM_DELETE_WINDOW", self.on_window_close)

        top.columnconfigure(1, weight=1)
        top.rowconfigure(1, weight=1)

        self.top_packer = tk.Frame(top, relief=tk.GROOVE, borderwidth=1)
        self.top_packer.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E)

        self.close_button = tk.Button(self.top_packer, text="Close",
                                       command=self.on_close_button_clicked)
        self.close_button.pack(side=tk.RIGHT)

        self.render_button = tk.Button(self.top_packer, text="Render",
                                       command=self.on_render_button_clicked)
        self.render_button.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(top, highlightbackground="black")
        self.canvas.grid(row=1, column=0, columnspan=2, sticky=tk.N+tk.W+tk.E+tk.S)

        self.play_button = tk.Button(top, text="Play", command=self.on_playpause_button_clicked)
        self.play_button.paused = True
        self.play_button.grid(row=2, column=0, sticky=tk.S)

        self.slider = tk.Scale(top, from_=0, to=self.video_frame_maker.duration,
                               orient=tk.HORIZONTAL,
                               resolution=1/(self.video_frame_maker.duration*self.fps))
        self.slider.grid(row=2, column=1, sticky=tk.N+tk.S+tk.W+tk.E)

        self.progress_bar = ProgressBar(top, fill="#00FF00", height=25)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=tk.S+tk.W+tk.E)

        self.canvas_area = Rectangle()
        self.canvas.image = None

        self.slider_alaram_period = int(1000/self.fps)
        self.frame_alaram_period = self.slider_alaram_period*5
        self.frame_alarm = self.top.after(self.frame_alaram_period, self.show_frame)
        self.slider_alarm = None
        self.render_alarm = None

    def move_forward(self):
        self.slider.set(self.slider.get()+1/self.fps)
        if self.slider_alarm:
            self.slider_alarm = self.top.after(int(1000/self.fps), self.move_forward)

    def show_frame(self):
        if self.video_process:
            if not self.video_process.is_alive():
                self.video_process = None
                self.play_button["state"] = "normal"
            else:
                self.slider.set(self.video_process.elapsed.value)
                self.progress_bar.set_progress(
                    self.video_process.elapsed.value/self.video_frame_maker.duration)

        t = self.slider.get()
        self.canvas_area.set_values(
            x2=self.canvas.winfo_width(), y2=self.canvas.winfo_height())
        image = self.video_frame_maker.get_image_at(t)
        self.canvas_image = CanvasImage(image, self.canvas_area)
        if self.canvas.image:
            self.canvas.delete(self.canvas.image)

        self.canvas.image = self.canvas.create_image(
                self.canvas_image.offset.x, self.canvas_image.offset.y,
                image=self.canvas_image.tk_image, anchor="nw")
        self.frame_alarm = self.top.after(self.frame_alaram_period, self.show_frame)

    def set_play_state(self, play):
        if play:
            self.slider_alarm = self.top.after(self.slider_alaram_period, self.move_forward)
            self.play_button.paused = False
            self.play_button["text"] = "Pause"
        else:
            self.slider_alarm = None
            self.play_button.paused = True
            self.play_button["text"] = "Play"

    def on_close_button_clicked(self):
        self.close()
        self.on_close_callback()

    def on_render_button_clicked(self):
        if self.video_process and self.video_process.is_alive():
            return
        video_filepath = filedialog.asksaveasfilename(filetypes=[("MP4", "*.mp4")])
        if video_filepath:
            self.progress_bar.set_text(video_filepath)
            self.set_play_state(False)
            self.play_button["state"] = "disable"
            self.render_alarm = self.top.after(self.slider_alaram_period, self.move_forward)
            if "-fopenmp" in wand.version.configure_options()["PCFLAGS"]:
                self.video_process = VideoThread(self.video_frame_maker, video_filepath, self.config)
            else:
                self.video_process = VideoProcess(self.video_frame_maker, video_filepath, self.config)
            self.video_process.start()

    def on_window_close(self):
        self.close()
        self.on_close_callback()

    def on_playpause_button_clicked(self):
        if self.play_button.paused:
            self.set_play_state(play=True)
        else:
            self.set_play_state(play=False)

    def close(self):
        if self.video_process:
            self.video_process.terminate()
        self.video_process = None
        self.top.destroy()