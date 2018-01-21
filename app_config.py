import configparser

class AppConfig:
    APP_SECTION = "app"

    def __init__(self, filepath):
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