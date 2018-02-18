import sys
import logging

from .configs import EnvironConfig
from .configs import LoggingConfig, AppConfig

def load_image_magick():
    if not EnvironConfig.is_magick_found():
        from .ui_tk.magick_home_loader import MagickHomeLoader
        app = MagickHomeLoader()
        app.mainloop()
    return EnvironConfig.is_magick_found()

def main():
    logging_config = LoggingConfig(AppConfig.FILENAME)
    logging_config.apply_on_logger(logging.getLogger())
    logging.info("Application Started.")

    if not load_image_magick():
        error_msg ="ImageMagick is not found! Aborting the program."
        logging.critical(error_msg)
        sys.exit(error_msg)
        return

    from .ui_tk.main_app import MainApp
    main_app = MainApp(title="Img2Vid", width=800, height=400)
    main_app.start()

    logging.info("Application Closed.")

    logging_config.close()
    try:
        sys.exit()
    except SystemExit:
        pass
