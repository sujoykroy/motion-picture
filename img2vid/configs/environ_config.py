import os
import traceback
import platform
import itertools
import logging
import ctypes.util

from .path_config import PathConfig

class EnvironConfig:
    FILENAME = "envion.ini"
    DEFAULT_SECTION = "default"
    MAGICK_HOME = "MAGICK_HOME"

    def __init__(self):
        self._parser = PathConfig.create_parser(self.FILENAME)

    def save(self):
        filepath = PathConfig.get_editable_filepath(self.FILENAME)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as filep:
            self._parser.write(filep)

    def set_variable(self, name, value):
        section = self.get_section(self.DEFAULT_SECTION)
        section[name] = value

    def get_variable(self, name):
        section = self.get_section(self.DEFAULT_SECTION)
        return section.get(name, "")

    def load_variable(self, name):
        value = self.get_variable(name)
        if value:
            os.environ[name] = value

    def get_section(self, section_name):
        if section_name not in self._parser:
            self._parser[section_name] = {}
        return self._parser[section_name]

    @staticmethod
    def get_magick_error():
        try:
            import wand.api#pylint: disable=unused-variable
        except ImportError:
            return str(traceback.format_exc())
        return ""

    @classmethod
    def is_magick_found(cls, load_var=False):
        if platform.system == "Drawin":
            found = False
            for path in ['', '/opt/', '/opt/local/']:
                if path:
                    config = cls()
                    config.set_variable(cls.MAGICK_HOME, path)
                    config.load_variable(cls.MAGICK_HOME)
                try:
                    import wand.api#pylint: disable=unused-variable
                except ImportError:
                    logging.getLogger(__name__).error(
                        "ImageMagick not found in path [{}]".format(path))
                    continue
                return True
        if load_var:
            config = cls()
            config.load_variable(cls.MAGICK_HOME)
        try:
            import wand.api#pylint: disable=unused-variable
        except ImportError:
            if not load_var:
                return cls.is_magick_found(load_var=True)
            return False
        return True


    def get_magick_names(self):
        versions = '', '-6', '-Q16', '-Q8', '-6.Q16'
        options = '', 'HDRI', 'HDRI-2'
        magick_home = self.get_variable(self.MAGICK_HOME)
        def magick_path(path):
            return os.path.join(magick_home, path)

        system = platform.system
        wand_names = []
        magick_names = []
        combinations = itertools.product(versions, options)

        for suffix in (version + option for version, option in combinations):
            if system == 'Windows':
                libwand = 'CORE_RL_wand_{0}.dll'.format(suffix)
                libmagick = 'CORE_RL_magick_{0}.dll'.format(suffix)
                wand_names.append(magick_path(libwand))
                magick_names.append(magick_path(libmagick))

                libwand = 'libMagickWand{0}.dll'.format(suffix)
                libmagick = 'libMagickCore{0}.dll'.format(suffix)

                wand_names.append(magick_path(libwand))
                magick_names.append(magick_path(libmagick))
            elif system == 'Darwin':
                libwand =  os.path.join('lib', 'libMagickWand{0}.dylib'.format(suffix))
                wand_names.append(magick_path(libwand))
            else:
                libwand = os.path.join('lib', 'libMagickWand{0}.so'.format(suffix))
                wand_names.append(magick_path(libwand))
                libwand = ctypes.util.find_library('MagickWand' + suffix)

        path_names = "Valid Wand library locations:\n" + "\n".join(wand_names)
        if magick_names:
            path_names += "\nValid Magick library locations:\n" + "\n".join(magick_names)
        return path_names
