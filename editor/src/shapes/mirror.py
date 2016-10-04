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
