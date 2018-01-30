import configparser

class AppConfig:
    APP_SECTION = "app"

    def __init__(self, filepath):
        self.temp_file_seed = 0
        self.filepath = filepath
        self.parser = configparser.ConfigParser()
        self.parser.read(filepath)

        if self.APP_SECTION in self.parser:
            self.app_section = self.parser[self.APP_SECTION]
        else:
            self.app_section = {}

        aspect_ratio_text = self.app_section.get("aspect-ratio", "16x9")
        ws, hs = aspect_ratio_text.split("x")[:2]
        self.aspect_ratio = float(ws)/float(hs)

        self.video_background_color = self.app_section.get("video-bg-color", "#CCCCCC")
        self.text_background_color = self.app_section.get("text-bg-color", "#FF0000")
        self.text_foreground_color = self.app_section.get("text-fg-color", "#000000")
        self.text_font_name = self.app_section.get("text-font-name", "ariel")
        self.text_font_size = int(self.app_section.get("text-font-size", "12"))
        self.caption_background_color = self.app_section.get("caption-bg-color", "#FFFFFF44")
        self.caption_foreground_color = self.app_section.get("caption-fg-color", "#000000")

        self.ppi = int(self.app_section.get("ppi", 340))

        self.ffmpeg_params = self.app_section.get(
                "ffmpeg-params", "-quality good -qmin 10 -qmax 42").split(" ")
        self.bit_rate = self.app_section.get("bit-rate", "640k")
        self.ffmpeg_preset = self.app_section.get("ffmpeg-preset", "superslow")
        self.video_codec = self.app_section.get("video-codec", "mpeg4")
        self.fps = int(self.app_section.get("fps", 25))

        exts = self.app_section.get("image-extensions",
                                    ".jpg, .jpeg, .JPG, .JPEG, .png").split(",")
        self.image_extensions = []
        for ext in exts:
            ext = ext.strip()
            if ext:
                self.image_extensions.append(ext)

    def get_font_tuple(self):
        return (self.text_font_name, self.text_font_size)

    def get_param(self, param_name, default_value):
        return self.app_section.get(param_name, default_value)

    def get_video_resolution(self):
        w, h = self.app_section.get("video-resolution", "1280x720").split("x")
        return (int(w), int(h))

    def get_image_types(self):
        types = []
        for ext in self.image_extensions:
            types.append("*" + ext)
        return ", ".join(types)

    def get_font(self):
        return "{0} {1}".format(self.text_font_name, self.text_font_size)