import configparser

class AppConfig:
    APP_SECTION = "app"

    def __init__(self, filepath):
        self.temp_file_seed = 0
        self.filepath = filepath
        self.parser = configparser.ConfigParser()
        self.parser.read(filepath)

        if AppConfig.APP_SECTION in self.parser:
            self.app_section = self.parser[APP_SECTION]
        else:
            self.app_section = {}

        aspect_ratio_text = self.app_section.get("aspect-ratio", "16x9")
        ws, hs = aspect_ratio_text.split("x")[:2]
        self.aspect_ratio = float(ws)/float(hs)

        self.video_background_color = self.app_section.get("video-bg-color", "#FFFFFF")
        self.text_background_color = self.app_section.get("text-bg-color", "#FF0000")
        self.text_foreground_color = self.app_section.get("text-fg-color", "#FFFFFF")
        self.text_font_name = self.app_section.get("text-font-name", "ariel")
        self.text_font_size = int(self.app_section.get("text-font-size", "22"))

    def get_font_tuple(self):
        return (self.text_font_name, self.text_font_size)

    def get_param(self, param_name, default_value):
        return self.app_section.get(param_name, default_value)

    def get_video_resolution(self):
        w, h = self.app_section.get("video-resolution", "1280x720").split("x")
        return (int(w), int(h))