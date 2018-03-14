import os
import tkinter as tk

from .frame import Frame
from .image_editor import ImageEditor
from .slide_prop_editor import SlidePropEditor
from .slide_navigator import SlideNavigator
from .dialog import Dialog
from .preview_player import PreviewPlayer

from ..slides import TextSlide, ImageSlide, VideoSlide
from ..renderer import VideoRenderer

class SlideEditor(Frame):
    def __init__(self, master, app_config, project):
        super().__init__(
            master=master,
            app_config=app_config,
            event_names=[
                "close", "preview"
            ]
        )
        self._project = project
        self._slide_index = 0
        self._slide = None

        self.base.rowconfigure(1, weight=1)
        self.base.columnconfigure(0, weight=1)

        self.widgets.preview_player = None
        self.widgets.toolbar = tk.Frame(self.base)
        self.widgets.toolbar.grid(
            row=0, column=0, columnspan=2,
            stick=tk.W+tk.E)
        self.widgets.add_image_slide_btn = \
            self._add_tool_button(
                "Close",
                self._ask_for_closing,
                tk.RIGHT)

        self.widgets.add_image_slide_btn = \
            self._add_tool_button(
                "Preview",
                self._ask_for_preview,
                tk.RIGHT)

        self.widgets.add_text_slide_btn = \
            self._add_tool_button(
                "Add Text Slide",
                self._ask_for_text_slide,
                tk.LEFT)
        self.widgets.add_image_slide_btn = \
            self._add_tool_button(
                "Add Image Slide(s)",
                self._ask_for_image_slides,
                tk.LEFT)
        self.widgets.add_video_slide_btn = \
            self._add_tool_button(
                "Add Video Slide(s)",
                self._ask_for_video_slides,
                tk.LEFT)

        self.widgets.image_editor = ImageEditor(self.base, self.app_config)
        self.widgets.image_editor.grid(
            row=1, column=0, sticky=tk.N+tk.S+tk.W+tk.E)

        self.widgets.slide_navigator = SlideNavigator(self.base)
        self.widgets.slide_navigator.events.move_slide.bind(self.move_to_slide)
        self.widgets.slide_navigator.grid(row=2, column=0, sticky=tk.W+tk.E)

        self.widgets.slide_prop_editor = SlidePropEditor(self.base, app_config)
        self.widgets.slide_prop_editor.events.slide_updated.bind(self._slide_updated)
        self.widgets.slide_prop_editor.events.crop_slide.bind(self._crop_slide)
        self.widgets.slide_prop_editor.events.delete_slide.bind(self._delete_slide)
        self.widgets.slide_prop_editor.grid(
            row=1, column=1, rowspan=2, sticky=tk.N+tk.S)
        self.move_to_slide(0)

    def destroy(self):
        self.widgets.image_editor.destroy()
        super().destroy()

    def move_to_slide(self, incre=0):
        if self._project.slide_count == 0:
            self._slide = None
            self._slide_index = -1
        else:
            self._slide_index += incre
            self._slide_index %= self._project.slide_count
            self._slide = self._project.slides[self._slide_index]

        self.widgets.slide_prop_editor.set_slide(self._slide)
        self.widgets.image_editor.set_slide(self._slide)
        self.widgets.slide_navigator.set_info(
            self._slide_index, self._project.slide_count)

    def _slide_updated(self):
        self.widgets.image_editor.set_slide(self._slide)

    def _delete_slide(self):
        if self._project.slide_count == 1:
            Dialog.show_error(
                "Low slide count",
                "You need to keep at least one slide in the project.")
            return
        self._project.remove_slide(self._slide_index)
        self.move_to_slide()

    def _crop_slide(self):
        if not self._slide.crop_allowed:
            return
        rects = self.widgets.image_editor.get_region_rects()
        if not rects:
            return
        for rect in rects:
            new_slide = self._slide.crop(rect)
            self._project.add_slide(new_slide, after=self._slide_index)
        self.move_to_slide(1)

    def _ask_for_text_slide(self):
        text = Dialog.ask_for_text("Text Slide", "Enter text to display")
        if text:
            slide = TextSlide.new_with_text(text=text)
            self._project.add_slide(slide, before=self._slide_index)
            self.move_to_slide()
        else:
            error_msg = "You need to provide some text to create a text slide."
            Dialog.show_error("Error", error_msg)

    def _ask_for_image_slides(self):
        if isinstance(self._slide, ImageSlide):
            start_dir = os.path.dirname(self._slide.filepath)
        else:
            start_dir = None
        image_files = Dialog.ask_for_image_files(
            self.app_config.image_types, start_dir=start_dir)
        if image_files:
            count = 0
            for image_file in image_files:
                slide = ImageSlide(filepath=image_file)
                self._project.add_slide(slide, after=self._slide_index+count)
                count += 1
            self.move_to_slide(count)
        else:
            error_msg = "You have not selected any image to add."
            Dialog.show_error("Error", error_msg)

    def _ask_for_video_slides(self):
        if isinstance(self._slide, ImageSlide):
            start_dir = os.path.dirname(self._slide.filepath)
        else:
            start_dir = None
        video_files = Dialog.ask_for_video_files(
            self.app_config.video_types, start_dir=start_dir)
        if video_files:
            count = 0
            for video_file in video_files:
                slide = VideoSlide(filepath=video_file)
                self._project.add_slide(slide, after=self._slide_index+count)
                count += 1
            self.move_to_slide(count)
        else:
            error_msg = "You have not selected any video to add."
            Dialog.show_error("Error", error_msg)

    def _ask_for_closing(self):
        self._project.save()
        if self.widgets.preview_player:
            self.widgets.preview_player.close()
        self.events.close.fire()

    def _ask_for_preview(self):
        if self.widgets.preview_player:
            return
        video_renderer = VideoRenderer.create_from_project(
            self._project, self.app_config)
        player = PreviewPlayer(self.base.master, self.app_config, video_renderer)
        player.events.close.bind(self._delete_preview)
        self.widgets.preview_player = player

    def _delete_preview(self):
        if not self.widgets.preview_player:
            return
        self.widgets.preview_player = None

    def _add_tool_button(self, text, command, side):
        button = tk.Button(self.widgets.toolbar,
                           text=text, command=command)
        button.pack(side=side)
        return button
