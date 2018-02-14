from ..effects import EFFECT_TYPES

from .text_config import TextConfig
from .image_config import ImageConfig
from .effect_config import EffectConfig
from .debug_config import DebugConfig
from .video_render_config import VideoRenderConfig
from .path_config import PathConfig

class AppConfig:
    def __init__(self, filename="app.ini"):
        self._parser = PathConfig.create_parser(filename)

        section = self.get_section("general")
        ppi = int(section.get("ppi", 340))
        font_name = section.get("font-name", "Courier")
        font_size = section.get("font_size", "15")
        back_color = section.get("back-color", "#000000")

        section = self.get_section("editor")
        self.editor_back_color = section.get("back-color", "white")

        section = self.get_section("text-slide")
        self.text = TextConfig(
            font_name=section.get("font-name", font_name),
            font_size=section.get("font-size", font_size),
            font_color=section.get("font-color", "#FFFFFF"),
            back_color=section.get("back-color", back_color),
            ppi=ppi,
            duration=section.get("duration", 3))

        section = self.get_section("image-slide")
        self.image = ImageConfig(
            font_name=section.get("font-name", font_name),
            font_size=section.get("font-size", font_size),
            font_color=section.get("font-color", "#000000"),
            back_color=section.get("back-color", "#ffffffaa"),
            padding=section.get("padding", 0),
            ppi=ppi,
            min_crop_duration=section.get("min-crop-duration", 1),
            max_crop_duration=section.get("max-crop-duration", 2),
            crop_source_duration=section.get("crop-source-duration", 3),
            duration=section.get("duration", 5))

        section = self.get_section("video-render")
        video_width, video_height = section.get("resolution", "1280x720").split("x")
        self.video_render = VideoRenderConfig(
            width=int(video_width), height=int(video_height),
            ffmpeg_params=section.get(
                "ffmpeg-params",
                "-quality good -qmin 10 -qmax 42").split(" "),
            bit_rate=section.get("bit-rate", "640k"),
            ffmpeg_preset=section.get("ffmpeg-preset", "superslow"),
            video_codec=section.get("video-codec", "mpeg4"),
            fps=int(section.get("fps", 25)),
            back_color=back_color,
            video_ext=section.get("video-ext", ".mov"),
        )

        self.effects = {}
        for effect_name, effect_class in EFFECT_TYPES.items():
            section = self.get_section("effect-" + effect_name)
            key_values = {}
            for key, value in section.items():
                key_values[key] = value
            self.effects[effect_name] = EffectConfig(effect_class, key_values)

        section = self.get_section("debug")
        self.debug = DebugConfig(
            pan_trace=(section.get("pan-trace", "False") == "True")
        )

    def get_section(self, section_name):
        if section_name in self._parser:
            return self._parser[section_name]
        return {}

    @property
    def image_types(self):
        return (
            ("JPEG files", "*.jpg *.JPG *.jpeg *.JPEG"),
            ("PNG files", "*.png *.PNG"),
            ("All Files", "*.*")
        )

    @property
    def video_types(self):
        return (
            ("MOV files", "*.mov, *MOV"),
            ("MPEG files", "*.mpeg"),
            ("All Files", "*.*")
        )
