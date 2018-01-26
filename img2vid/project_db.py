import os
import json

from slides import ImageSlide, TextSlide

class ProjectDb:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.data = dict(slides=[])
        self.slides = self.data["slides"]
        if self.filepath and os.path.isfile(self.filepath):
            with open(self.filepath, "r") as f:
                data = json.load(f)
                for slide in data["slides"]:
                    if slide["type"] == TextSlide.TypeName:
                        slide = TextSlide.create_from_data(slide)
                    else:
                        slide = ImageSlide.create_from_data(slide)
                    self.add_slide(slide)
        self._update()

    def set_filepath(self, filepath):
        self.filepath = filepath

    def get_slide_at_index(self, index):
        return self.slides[index]

    def add_slide(self, slide, before=None, after=None):
        if before is not None:
            self.slides.insert(before, slide)
        elif after is not None:
            self.slides.insert(after+1, slide)
        else:
            self.slides.append(slide)
        self._update()

    def remove_slide(self, index):
        del self.slides[index]
        self._update()

    def add_image_files_from_dir(self, dir):
        for filename in os.listdir(dir):
            root, ext = os.path.splitext(filename)
            if ext in (".jpg", ".png"):
                filepath = os.path.join(dir, filename)
                slide = ImageSlide(filepath=filepath)
                self.add_slide(slide)

    def _update(self):
        self.slide_count = len(self.slides)

    def save(self):
        if not self.filepath:
            return
        with open(self.filepath, "w") as f:
            json.dump(self.data, f)
