import os
import configparser

ROOT_CONFIG_DIR = os.path.abspath(os.path.dirname(__file__))
LOCAL_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".img2vid")

class PathConfig:
    @staticmethod
    def get_filepaths(filename):
        return [
            os.path.join(ROOT_CONFIG_DIR, filename),
            os.path.join(LOCAL_CONFIG_DIR, filename),
        ]

    @staticmethod
    def get_editable_filepath(filename):
        return os.path.join(LOCAL_CONFIG_DIR, filename)

    @staticmethod
    def create_parser(filename):
        filepaths = PathConfig.get_filepaths(filename)
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(filepaths)
        return parser
