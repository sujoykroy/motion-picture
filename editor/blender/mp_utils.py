import bpy
import math
import mathutils
import numpy
PI_PER_DEG = math.pi/180.

def get_path_xy_values(filepath, time_frac, x_offset=0):
    xy_values = numpy.load(filepath)
    maxs = numpy.amax(xy_values, axis=1)[0]
    xy_values[:, :, 0] = xy_values[:, :, 0]/maxs[0]
    xy_values[:, :, 1] = xy_values[:, :, 1]/maxs[1]
    time_index_frac = (xy_values.shape[0]-1)*time_frac
    time_index = int(time_index_frac)
    path_xys = xy_values[time_index, :, :]
    if time_index != time_index_frac and time_index <xy_values.shape[0]-1:
        time_index_extra = time_index_frac-time_index
        path_xys = path_xys + (xy_values[time_index+1, :, :]-path_xys)*time_index_extra

    path_xys = path_xys + numpy.array([x_offset, 0, 0])
    return path_xys

class DrawingObject(object):
    NameSeed = 0

    def __init__(self, name):
        if name is None:
            name = u"do_{0}".format(DrawingObject.NameSeed)
            DrawingObject.NameSeed += 1
        self.name = name
        self.added_to_scene = False
        self.obj = None

    def add_to_scene(self, scene=None):
        if self.added_to_scene:
            return
        if scene is None:
            scene = bpy.context.scene
        scene.objects.link(self.obj)
        scene.objects.active = self.obj
        self.obj.select = True

    def rotate(self, x=0, y=0, z=0):
        self.obj.delta_rotation_euler = (x*PI_PER_DEG, y*PI_PER_DEG, z*PI_PER_DEG)

    def move_to(self, x=0, y=0, z=0):
        self.obj.delta_location = (x, y, z)

    def scale(self, x=1, y=1, z=1, xyz=None):
        if xyz:
            x = y = z = xyz
        self.obj.delta_scale= (x, y, z)

class Mesh(DrawingObject):
    CurrentScene = None

    def __init__(self, name=None):
        super(Mesh, self).__init__(name)
        self.mesh = bpy.data.meshes.new(self.name)
        self.obj = bpy.data.objects.new(self.name, self.mesh)
        self.add_to_scene()

    def fill_with_data(self, verts, edges, faces):
        self.mesh.from_pydata(verts, edges, faces)
        self.mesh.update()

    def make_cube(self):
        verts = [
            [-1, 1, -1], [1, 1, -1], [1, -1, -1], [-1, -1, -1],
            [-1, 1, 1], [1, 1, 1], [1, -1, 1], [-1, -1, 1],
        ]
        faces = [
            [0, 1, 2, 3], [4, 7, 6, 5],
            [0, 4, 5, 1], [1, 5, 6 , 2],
            [2, 3, 7, 6], [0, 3, 7, 4]
        ]
        self.fill_with_data(verts, [], faces)

    def make_rod(self, from_loc, to_loc, radius, radius_steps):
        face_indices = list(range(radius_steps))
        faces = []
        lower_verts = []
        upper_verts = []
        span = to_loc-from_loc

        angle_step = 2*math.pi/radius_steps
        for i in range(radius_steps):
            angle = angle_step*i
            x = radius*math.cos(angle)
            y = radius*math.sin(angle)
            lower_verts.append((x, y, 0))
            upper_verts.append((x, y, span.length))
            if i <radius_steps-1:
                faces.append((i, i+1, i+radius_steps+1, i+radius_steps))
            else:
                faces.append((i, i-radius_steps+1, i+1, i+radius_steps))
        verts = lower_verts+upper_verts
        self.fill_with_data(verts, [], faces)
        self.move_to(*from_loc)
        self.obj.rotation_mode = 'QUATERNION'
        self.obj.rotation_quaternion = span.to_track_quat('Z', 'Y')

    @staticmethod
    def get_spherical_verts_faces(horiz_steps, vert_steps, sphere_top=1, radius=1):
        faces = []
        upper_points = []
        lower_points = []
        angle_step = 360./horiz_steps
        upper_points_count = (vert_steps+sphere_top)*horiz_steps
        for vi in range(vert_steps+sphere_top):
            vfrac = (vi*1./vert_steps)
            xy_radius = radius*math.cos(vfrac*math.pi*.5)
            z = radius*math.sin(vfrac*math.pi*.5)
            for hi in range(horiz_steps):
                angle = 2*math.pi*hi*1./horiz_steps
                x = xy_radius*math.cos(angle)
                y = xy_radius*math.sin(angle)
                upper_points.append([x, y, z])
                lower_points.append([x, y, -z])

                if vi>=(vert_steps-1+sphere_top):
                    continue
                if hi<horiz_steps-1:
                    pi = vi*horiz_steps+hi
                    faces.append([pi, pi+1, pi+1+horiz_steps, pi+horiz_steps])
                    pi += upper_points_count
                    faces.append([pi, pi+horiz_steps, pi+horiz_steps+1, pi+1])

                else:
                    pi = vi*horiz_steps+hi
                    faces.append([pi, pi-horiz_steps+1, pi+1, pi+horiz_steps])
                    pi += upper_points_count
                    faces.append([pi, pi+horiz_steps, pi+1, pi-horiz_steps+1])
        verts = upper_points + lower_points
        return (verts, faces)

    def make_sphere(self, horiz_steps, vert_steps, radius_steps=1, radius=1, sphere_top=1):
        if radius_steps == 1:
            verts, faces = self.get_spherical_verts_faces(horiz_steps, vert_steps, radius=radius, sphere_top=sphere_top)
        else:
            verts = []
            for ri in range(radius_steps):
                frac = (ri+1)*1./radius_steps
                lverts, lfaces = self.get_spherical_verts_faces(
                    max(int(horiz_steps*frac), 1), max(int(vert_steps*frac), 1),
                    radius=radius*frac, sphere_top=sphere_top)
                verts.extend(lverts)
            faces = []
        #print(radius_steps, faces)
        self.fill_with_data(verts, [], faces)

    def make_disc(self, steps, radius=1):
        faces = []
        verts = [[0,0,0]]
        edges = []
        angle_step = 2*math.pi/steps
        for hi in range(steps):
            angle = hi*angle_step
            x = radius*math.cos(angle)
            y = radius*math.sin(angle)
            verts.append([x, y, 0])

            if hi<steps-1:
                faces.append([hi+1, hi+2, 0])
                edges.append([hi+1, hi+2])
            else:
                faces.append([hi+1, 1, 0])
                edges.append([hi+1, 1])
        self.fill_with_data(verts, edges, faces)



    def fill_from_path(self, path_xy_filepath, time_frac=0, line_divs=-1, round_divs=4, x_offset=0):
        path_xys = get_path_xy_values(path_xy_filepath, time_frac, x_offset)

        angle_step  = math.pi*2./round_divs
        circle_xy_values = numpy.zeros(0)
        for ai in range(round_divs):
            angle = ai*angle_step
            x = math.cos(angle)
            y = math.sin(angle)
            circle_xy_values = numpy.append(circle_xy_values, (x, y))
        circle_xy_values.shape = (-1, 2)

        verts = []
        faces = []
        edges = []

        if line_divs <= 0 or line_divs>path_xys.shape[0]:
            line_divs = path_xys.shape[0]

        line_indices = numpy.linspace(0, path_xys.shape[0]-1, line_divs, endpoint=True, dtype=numpy.int)
        self.layer_vert_indices = []
        for li in range(len(line_indices)):
            path_xy = path_xys[line_indices[li], :2]
            z = path_xy[1]
            xys = circle_xy_values * (path_xy[0] + x_offset)

            circle_vert_indices = []
            for ri in range(round_divs):
                xy = xys[ri, :]
                circle_vert_indices.append(len(verts))
                verts.append((xy[0], xy[1], z))
                if li>=len(line_indices)-1:
                    continue
                pi = li*round_divs+ri
                if ri<round_divs-1:
                    faces.append([pi, pi+1, pi+1+round_divs, pi+round_divs])
                    edges.extend([
                            [pi, pi+1],
                            [pi+1, pi+1+round_divs],
                            [pi+1+round_divs, pi+round_divs],
                            [pi+round_divs, pi]
                    ])
                else:
                    faces.append([pi, pi-round_divs+1, pi+1, pi+round_divs])
                    edges.extend([
                            [pi, pi-round_divs+1],
                            [pi-round_divs+1, pi+1],
                            [pi+1, pi+round_divs],
                            [pi+round_divs, pi]
                    ])
            self.layer_vert_indices.append(circle_vert_indices)
        self.fill_with_data(verts, edges, faces)

class Curve(DrawingObject):
    def __init__(self, name=None):
        super(Curve, self).__init__(name)
        self.curve = bpy.data.curves.new(self.name, 'CURVE')
        self.obj = bpy.data.objects.new(self.name, self.curve)
        self.add_to_scene()

    def make_ring(self, radius=1):
        spline = self.curve.splines.new('BEZIER')
        spline.bezier_points.add(3)
        self.curve.dimensions = "3D"
        spline.use_cyclic_u = True

        k = .5522847498*.5#magic number
        bezier_points = [
            [(-radius*1., -radius*k), (-radius*1, radius*k), (-radius*1, 0.)],
            [(-radius*k, radius*1.), (radius*k, 1.), (0., radius*1)],
            [(radius*1., radius*k), (radius*1., -radius*k), (radius*1., 0.)],
            [(radius*k, -radius*1), (-radius*k, -radius*1), (0., -radius*1.)],
        ]
        for i in range(len(bezier_points)):
            bzp = bezier_points[i]
            sbzp = spline.bezier_points[i]
            sbzp.co = (bzp[2][0], bzp[2][1], 0.)
            sbzp.handle_left = (bzp[0][0], bzp[0][1], 0.)
            sbzp.handle_right = (bzp[1][0], bzp[1][1], 0.)
            sbzp.handle_left_type = "AUTO"
            sbzp.handle_right_type = "AUTO"

        self.curve.fill_mode = "FULL"
        self.curve.bevel_depth = .12

    def add_line(self, from_loc, to_loc, div=1):
        from_loc = mathutils.Vector(from_loc)
        to_loc = mathutils.Vector(to_loc)
        diff_loc = to_loc-from_loc


        spline = self.curve.splines.new('BEZIER')
        spline.bezier_points.add(div+1)
        self.curve.dimensions = "3D"

        self.curve.bevel_depth = .1
        self.curve.bevel_resolution = 1

        frac_step = 1./((div+1)*3)
        for i in range(div+2):
            dest_frac =  i*1./(div+1)
            left_hand_frac = dest_frac-frac_step
            right_hand_frac = dest_frac+frac_step

            bzp = spline.bezier_points[i]
            bzp.co = from_loc + diff_loc*dest_frac
            bzp.handle_left = from_loc + diff_loc*left_hand_frac
            bzp.handle_right = from_loc + diff_loc*right_hand_frac

            bzp.handle_left_type = "AUTO"
            bzp.handle_right_type = "AUTO"

        self.curve.fill_mode = "FULL"
