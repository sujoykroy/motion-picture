"""This module handle project database management"""
import os
import re
import json

import requests

from .slide import Slide
from .image_slide import ImageSlide
from .video_slide import VideoSlide
from .text_slide import TextSlide
from .geom_slide import RectGeomSlide, CircleGeomSlide

class Project:
    """This class stores slides information for a given project.
    """
    KEY_SLIDES = "slides"
    URL_PATH_RE = re.compile(r'https?://')

    def __init__(self):
        self.slides = []
        self.filepath = None

    def add_image_files(self, image_files, after_index=None):
        count = 0
        for filepath in image_files:
            slide = ImageSlide(filepath=filepath)
            self.add_slide(slide, after=after_index)
            count += 1
        return count

    @property
    def slide_count(self):
        """Returns number of slides."""
        return len(self.slides)

    def get_slide_at_index(self, index):
        """returns slide at a index position"""
        return self.slides[index]

    def add_slide(self, slide, before=None, after=None):
        """"Adds slide, before or after given slide.
        If before or after is not specified,
        slide will be appended at the last."""
        if before is not None:
            self.slides.insert(before, slide)
        elif after is not None:
            self.slides.insert(after+1, slide)
        else:
            self.slides.append(slide)

    def remove_slide(self, index):
        """Remove slide from the given index postion."""
        del self.slides[index]

    def load_from(self, filepath):
        """Load slides from the given filepath."""
        project_data = None
        if self.URL_PATH_RE.match(filepath):
            resp = requests.get(filepath)
            project_data = json.loads(resp.text)
        else:
            self.filepath = filepath
            _, ext = os.path.splitext(filepath)
            if ext == ".json":
                with open(filepath, "r") as file_ob:
                    project_data = json.load(file_ob)

        if project_data:
            self.load_from_json(project_data)

    def load_from_json(self, project_data):
        """Load slides from the given json data."""
        slides_data = project_data.get(self.KEY_SLIDES, [])
        for slide_data in slides_data:
            slide = self.create_slide_from_json(slide_data)
            if slide:
                self.add_slide(slide)

    def save(self, filepath=None):
        if not self.slides:
            return
        if not filepath:
            filepath = self.filepath
        elif not self.filepath:
            self.filepath = filepath
        if not filepath:
            return
        _, ext = os.path.splitext(filepath)
        if ext == ".json":
            project_data = {}
            slides_data = []
            project_data[self.KEY_SLIDES] = slides_data
            for slide in self.slides:
                slides_data.append(slide.get_json())
            with open(filepath, "w") as file_ob:
                json.dump(project_data, file_ob, indent=4)

    @classmethod
    def create_slide_from_json(cls, data):
        slide = None
        if Slide.KEY_TYPE in data:
            slide_type = data[Slide.KEY_TYPE]
            if slide_type == TextSlide.TYPE_NAME:
                slide = TextSlide.create_from_json(data)
            elif slide_type == VideoSlide.TYPE_NAME:
                slide = VideoSlide.create_from_json(data)
            elif slide_type == ImageSlide.TYPE_NAME:
                slide = ImageSlide.create_from_json(json.loads(json.dumps(data)))
                if VideoSlide.check_if_file_supported(slide.filepath):
                    slide = VideoSlide.create_from_json(data)
            elif slide_type == RectGeomSlide.TYPE_NAME:
                slide = RectGeomSlide.create_from_json(data)
            elif slide_type == CircleGeomSlide.TYPE_NAME:
                slide = CircleGeomSlide.create_from_json(data)
            if data.get(Slide.KEY_MASK_SLIDE):
                mask_slide = cls.create_slide_from_json(data[Slide.KEY_MASK_SLIDE])
                slide.set_mask_slide(mask_slide)
            if data.get(Slide.KEY_SUB_SLIDES):
                for sub_slide in data.get(Slide.KEY_SUB_SLIDES):
                    sub_slide = cls.create_slide_from_json(sub_slide)
                    slide.add_sub_slide(sub_slide)
        return slide
