"""This modules holds the configurations for application wide Logging"""
import logging
import logging.handlers

from .path_config import PathConfig

class LoggingConfig:
    _FILENAME = "var.log"
    _SECTION_NAME = "logging"

    _LEVELS = dict(
        CRITICAL=50, ERROR=40, WARNING=30,
        INFO=20, DEBUG=10, NOTSET=0)

    def __init__(self, filename):
        parser = PathConfig.create_parser(filename)
        if self._SECTION_NAME not in parser:
            parser[self._SECTION_NAME] = {}
        self._params = parser[self._SECTION_NAME]

        if not self.enabled:
            base_handler = logging.NullHandler()
        else:
            base_handler = logging.handlers.RotatingFileHandler(
                filename=PathConfig.get_editable_filepath(self.filename),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(msg)s')
            base_handler.setFormatter(formatter)

        self._handlers = [base_handler]
        if self.console:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(msg)s')
            console_handler.setFormatter(formatter)
            self._handlers.append(console_handler)

        for handler in self._handlers:
            handler.setLevel(self.level)

    def apply_on_logger(self, logger):
        for handler in self._handlers:
            logger.addHandler(handler)

    @property
    def enabled(self):
        return self._params.get("enabled", "False") == "True"

    @property
    def console(self):
        return self._params.get("console", "False") == "True"

    @property
    def level(self):
        level = self._params.get("level", "INFO")
        return self._LEVELS.get(level.upper(), 0)

    @property
    def max_bytes(self):
        return int(self._params.get("max-bytes", 1024*1024))

    @property
    def filename(self):
        return self._params.get("filename", self._FILENAME)

    @property
    def backup_count(self):
        return self._params.get("backup-count", self._FILENAME)

    def close(self):
        for handler in self._handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

        del self._handlers[:]
