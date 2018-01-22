import os

from slides import ImageSlide

class ProjectDb:
    def __init__(self, filepath):
        self.filepath = filepath
        if os.path.isfile(self.filepath):
            with open(self.filepath, "r") as f:
                self.data = json.load(f)
        else:
            self.data = dict(slides=[])
        self.slides = self.data["slides"]

    def get_slide_at_index(self, index):
        return self.slides[index]

    def add_slide(self, slide, before=None):
        if before is not None:
            self.slides.insert(before, slide)
        else:
            self.slides.append(slide)
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
            json.dump(f)
