import configparser

MAGICK_HOME="magick-home"

class EnvironConfig:
    def __init__(self, filepath):
        self.filepath = filepath
        self.parser = configparser.ConfigParser()
        self.parser.read(filepath)

    def get_magick_home(self):
        return self.parser.get("default", MAGICK_HOME, fallback="")

    def set_magick_home(self, path):
        self.parser.set("default", MAGICK_HOME, path)
        with open(self.filepath, "w") as f:
            self.parser.write(f)

