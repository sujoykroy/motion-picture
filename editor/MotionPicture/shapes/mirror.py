MIRROR_NONE = 0
MIRROR_X = -1
MIRROR_Y = -2
MIRROR_XY = -3
MIRROR_ALL = -4
MIRROR_ANGLE = -10

class Mirror(object):
    def __init__(self):
        self.mirror = 0
        self.mirror_angle = 0

    def get_scales_n_rotations(self):
        scales = []
        rotations = []

        if self.mirror == MIRROR_X or self.mirror == MIRROR_ALL:
            scales.append([-1, 1])
        if self.mirror == MIRROR_Y or self.mirror == MIRROR_ALL:
            scales.append([1, -1])
        if self.mirror == MIRROR_XY or self.mirror == MIRROR_ALL:
            scales.append([-1, -1])

        if self.mirror == MIRROR_ANGLE and self.mirror_angle>0:
            angle = self.mirror_angle
            while angle<360:
                rotations.append(angle)
                angle += self.mirror_angle
        return scales, rotations

    @staticmethod
    def set_xml_element(ob, elm):
        if ob.mirror == 0: return
        elm.attrib["mirror"] = "{0}".format(ob.mirror)
        elm.attrib["mirror_angle"] = "{0}".format(ob.mirror_angle)

    @staticmethod
    def assign_params_from_xml_element(ob, elm):
        ob.mirror = int(elm.attrib.get("mirror", MIRROR_NONE))
        ob.mirror_angle = float(elm.attrib.get("mirror_angle", 0))

    @staticmethod
    def copy_into(ob, newob):
        newob.mirror = ob.mirror
        newob.mirror_angle = ob.mirror_angle
