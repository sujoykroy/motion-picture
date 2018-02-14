"""This module handle project database management"""
import os
import json

from .slide import Slide
from .image_slide import ImageSlide
from .text_slide import TextSlide

class Project:
    """This class stores slides information for a given project.
    """
    KEY_SLIDES = "slides"

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
        self.filepath = filepath
        _, ext = os.path.splitext(filepath)
        if ext == ".json":
            with open(filepath, "r") as file_ob:
                project_data = json.load(file_ob)
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
                json.dump(project_data, file_ob)

    @staticmethod
    def create_slide_from_json(data):
        if Slide.KEY_TYPE in data:
            slide_type = data[Slide.KEY_TYPE]
            if slide_type == TextSlide.TYPE_NAME:
                return TextSlide.create_from_json(data)
            if slide_type == ImageSlide.TYPE_NAME:
                return ImageSlide.create_from_json(data)
        return None
