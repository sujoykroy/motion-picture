import os

TOP_INFO_BAR_TEXT_COLOR = "598ab8"
APP_VERSION = 0.1
APP_NAME = "MotionPicture"

_THIS_FOLDER = os.path.dirname(__file__)
_PARENT_FOLDER = os.path.dirname(_THIS_FOLDER)
ICONS_FOLDER = os.path.join(_PARENT_FOLDER, "icons")
MAIN_CSS_FILE = os.path.join(_THIS_FOLDER, "main_style.css")
PREDRAWN_SHAPE_FOLDER = os.path.join(ICONS_FOLDER, "predrawns")

