import os
import configparser

ROOT_CONFIG_DIR = os.path.abspath(os.path.dirname(__file__))
LOCAL_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".img2vid")

if not os.path.isdir(LOCAL_CONFIG_DIR):
    os.makedirs(LOCAL_CONFIG_DIR)

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
        """Returns configparse for given filename.
        filename will be searched inside app and in user local folder.
        The settings in later will override that of previous.

        :param filename: Name of the file to read from
        :type filename: `str`
        :rtype: `ConfigParser`
        """
        filepaths = PathConfig.get_filepaths(filename)
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(filepaths)
        return parser
