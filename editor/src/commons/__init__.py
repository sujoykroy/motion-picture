from point import Point
from colors import *
from curves import Curve
from polygon import Polygon
from bezier_point import BezierPoint
from rect import Rect
from ordered_dict import OrderedDict
from misc import *
from draw_utils import *
import math

RAD_PER_DEG = math.pi/180.

def get_displayble_prop_name(prop_name):
    label_words = prop_name.replace("_", " ").split(" ")
    for i in range(len(label_words)):
        label_words[i] = label_words[i][0].upper() + label_words[i][1:]
    return " ".join(label_words)
