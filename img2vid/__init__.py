import sys

from .configs import EnvironConfig

def load_image_magick():
    if not EnvironConfig.is_magick_found():
        from .ui_tk.magick_home_loader import MagickHomeLoader
        app = MagickHomeLoader()
        app.mainloop()
    return EnvironConfig.is_magick_found()

def main():
    if not load_image_magick():
        sys.exit("ImageMagick is not found! Aborting the program.")
        return

    from .ui_tk.main_app import MainApp
    main_app = MainApp(title="Img2Vid", width=800, height=400)
    main_app.start()
    try:
        sys.exit()
    except SystemExit:
        pass
