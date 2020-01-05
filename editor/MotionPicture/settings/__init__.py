from .config import *
from .menus import TopMenuItem
from .directory import Directory

class EditingChoice:
    LOCK_SHAPE_MOVEMENT = False
    LOCK_XY_GLOBAL = True
    LOCK_XY_MOVEMENT = None
    LOCK_GUIDES = False
    HIDE_GUIDES = False
    HIDE_CONTROL_POINTS = False
    HIDE_AXIS = True
    SHOW_ALL_TIME_LINES = True
    FREE_ERASING = False
    TIME_STEP = .1
    SHOW_POINT_GROUPS = True
    LOCK_SHAPE_SELECTION = False
    COHESIVE_MARKER_MOVEMENT = True
    LOCK_MARKERS = True
    LOCK_POINT_GROUP = False
    DISABLE_AUDIO = False
    HIDE_BACKGROUND_SHAPES = False
