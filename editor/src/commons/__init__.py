from point import Point
from colors import *
from curves import NaturalCurve, Curve, CurvePoint, CurvePointGroup
from polygon import Polygon, PolygonsForm
from bezier_point import BezierPoint
from rect import Rect
from ordered_dict import OrderedDict
from misc import *
from draw_utils import *
import math
from threshold import Threshold
from timer_clock import TimerClock

from point3d import Point3d
from object3d import Object3d
from polygon3d import Polygon3d
from polygroup3d import PolyGroup3d
from camera3d import Camera3d
from texture_map_color import TextureResources
from texture_map_color import TextureMapColor
from container3d import Container3d

from audio_message import AudioMessage

RAD_PER_DEG = math.pi/180.

def get_displayble_prop_name(prop_name):
    label_words = prop_name.replace("_", " ").split(" ")
    for i in range(len(label_words)):
        label_words[i] = label_words[i][0].upper() + label_words[i][1:]
    return " ".join(label_words)
