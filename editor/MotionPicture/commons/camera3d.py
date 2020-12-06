import numpy, cairo, math
from scipy import ndimage

from .object3d import Object3d
from .point3d import Point3d
from .polygon3d import Polygon3d
from .draw_utils import *
from .colors import hsv_to_rgb, rgb_to_hsv

def surface2array(surface):
    data = surface.get_data()
    if not data:
        return None
    rgb_array = 0+numpy.frombuffer(surface.get_data(), numpy.uint8)
    rgb_array.shape = (surface.get_height(), surface.get_width(), 4)
    #rgb_array = rgb_array[:,:,[2,1,0,3]]
    #rgb_array = rgb_array[:,:, :3]
    return rgb_array

class Camera3d(Object3d):
    def __init__(self, viewer=(0,0,0)):
        super(Camera3d, self).__init__()
        self.viewer = Point3d.create_if_needed(viewer)
        self.sorted_items = []
        self.mat_params = None
        self.hit_alpha = 0
        self.convolve_kernel = 0
        self.hsv_coef = None

    def project_point_values(self, point_values):
        point_values = self.forward_transform_point_values(point_values)
        return self.viewer_point_values(point_values)

    def viewer_point_values(self, point_values):
        if self.viewer.get_z() != 0:
            ratio = self.viewer.get_z()/point_values[:, 2]
            x_values = (ratio*point_values[:,0]) - self.viewer.get_x()
            y_values = (ratio*point_values[:,1]) - self.viewer.get_y()
            return numpy.stack((x_values, y_values), axis=1)
        else:
            return point_values[:, [0,1]]

    def reverse_project_point_value(self, point_value, z_depth):
        real_point_value = Point3d(x=point_value[0], y=point_value[1], z=z_depth)
        if self.viewer.get_z() != 0:
            ratio = z_depth/self.viewer.get_z()
            real_point_value.values[0] = (point_value[0] + self.viewer.get_x())/ratio
            real_point_value.values[1] = (point_value[1] + self.viewer.get_y())/ratio
        real_point_value.values = self.reverse_transform_point_values(real_point_value.values)
        return real_point_value.values

    def sort_items(self, items=None):
        polygons = []
        if items is None:
            polygons.extend(Polygon3d.Items)
        else:
            for item in items:
                if not hasattr(item, "polygons"):
                    continue
                polygons.extend(item.polygons)
        self.sorted_items = sorted(polygons, key=self.z_depth_sort_key)

        self.poly_face_params = None
        for item in self.sorted_items:
            params = numpy.array([item.plane_params_normalized[self]])
            if self.poly_face_params is None:
                self.poly_face_params = params
            else:
                self.poly_face_params = numpy.concatenate(
                        (self.poly_face_params, params), axis=0)

    def z_depth_sort_key(self, ob):
        return ob.z_depths[self]

    def get_image_canvas(self, left, top, width, height, border_color=None, border_width=None, scale=.5):
        left = math.floor(left)
        top = math.floor(top)
        width = int(width)
        height = int(height)
        if border_width>0:
            border_width = max(border_width*scale, 1)
        min_depth = -100000

        canvas_width = int(width*scale)
        canvas_height = int(height*scale)
        pixel_count = canvas_width*canvas_height
        canvas_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, canvas_width, canvas_height)
        canvas_surf_array = surface2array(canvas_surf)

        canvas_z_depths =numpy.repeat(min_depth, pixel_count)
        canvas_z_depths = canvas_z_depths.astype("f").reshape(canvas_height, canvas_width)

        obj_pad = max(border_width*4, 0)

        for object_3d in self.sorted_items:
            if object_3d.border_width:
                pad = max(obj_pad, object_3d.border_width*2)
            else:
                pad = obj_pad

            brect = object_3d.bounding_rect[self]
            bleft, btop = int(math.ceil(brect[0][0])), int(math.ceil(brect[0][1]))
            bright, bbottom = int(math.ceil(brect[1][0])), int(math.ceil(brect[1][1]))

            if bleft>left+width or bright<left or \
               btop>top+height or bbottom<top:
                continue

            bleft -= pad
            bright += pad
            btop -= pad
            bbottom += pad

            sleft = max(left, bleft)
            stop = max(top, btop)
            sright = min(left+width, bright)
            sbottom = min(top+height, bbottom)

            #if sleft>=sright or stop>=sbottom:
            #    continue

            sw = int(math.ceil(sright-sleft))
            sh = int(math.ceil(sbottom-stop))

            if sw<=0 or sh<=0:
                continue

            poly_canvas_width = int(sw*scale)
            poly_canvas_height = int(sh*scale)

            cleft = int((sleft-left)*scale)
            cright = min(int((sright-left)*scale), canvas_width)
            ctop = int((stop-top)*scale)
            cbottom = int((sbottom-top)*scale)

            if (ctop-cbottom!=poly_canvas_height):
                cbottom=poly_canvas_height+ctop
            if cbottom>canvas_height:
                cbottom = canvas_height
                ctop = cbottom-poly_canvas_height

            if (cright-cleft!=poly_canvas_width):
                cright=poly_canvas_width+cleft
            if cright>canvas_width:
                cright = canvas_width
                cleft = cright-poly_canvas_width

            #print "poly_canvas_height", poly_canvas_height, "poly_canvas_width", poly_canvas_width
            #print "cbottom-ctop", cbottom-ctop, "cright-cleft", cright-cleft
            #print "canvas_width, canvas_height", canvas_width, canvas_height
            #print "cbottom, ctop", cbottom, ctop, "cright, cleft", cright, cleft

            poly_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, poly_canvas_width, poly_canvas_height)
            poly_ctx = cairo.Context(poly_surf)
            poly_ctx.scale(scale, scale)
            set_default_line_style(poly_ctx)
            poly_ctx.rectangle(0, 0, sw, sh)
            poly_ctx.set_source_rgba(1, 0, 0, 0)
            poly_ctx.fill()
            poly_ctx.translate(-bleft, -btop)
            poly_ctx.translate(-(sleft-bleft), -(stop-btop))
            object_3d.draw(poly_ctx, self, border_color=border_color, border_width=border_width)

            surfacearray = surface2array(poly_surf)
            if surfacearray is None:
                continue
            area_cond = (surfacearray[:, :, 3]<=self.hit_alpha)

            xs = numpy.linspace(sleft, sright, poly_canvas_width)
            xcount = len(xs)
            ys = numpy.linspace(stop, sbottom, poly_canvas_height)
            ycount = len(ys)

            xs, ys = numpy.meshgrid(xs, ys)
            coords = numpy.vstack((xs.flatten(), ys.flatten()))
            coords = coords.T#.reshape((ycount, xcount, 2))
            coords.shape = (xcount*ycount, 2)

            vz = self.viewer.get_z()
            if vz == 0:
                coords_depths = numpy.matmul(object_3d.plane_params_normalized[self],
                    numpy.concatenate((coords.T, [numpy.ones(coords.shape[0])]), axis=0))
            else:
                vx = self.viewer.get_x()
                vy = self.viewer.get_y()
                pp = object_3d.plane_params_normalized[self]
                coords_depths = pp[2]*vz/(-pp[0]*(coords[:, 0]+vx)-pp[1]*(coords[:, 1]+vy)+vz)
                coords_depths.shape = (ycount, xcount)

            coords_depths.shape = (ycount, xcount)
            blank_depths = numpy.repeat(min_depth+1, ycount*xcount)
            blank_depths.shape = coords_depths.shape
            coords_depths = numpy.where(area_cond, blank_depths, coords_depths)

            pre_depths = canvas_z_depths[ctop:cbottom, cleft:cright]
            pre_depths.shape = (cbottom-ctop, cright-cleft)
            depths_cond = pre_depths<coords_depths#highier depths come at top

            new_depths = numpy.where(depths_cond, coords_depths, pre_depths)
            canvas_z_depths[ctop:cbottom, cleft:cright] = new_depths

            pre_colors = canvas_surf_array[ctop:cbottom, cleft:cright, :]
            pre_colors.shape = (cbottom-ctop, cright-cleft, 4)

            depths_cond_multi = numpy.repeat(depths_cond, 4)
            depths_cond_multi.shape = (depths_cond.shape[0], depths_cond.shape[1], 4)

            new_colors = numpy.where(depths_cond_multi, surfacearray, pre_colors)
            canvas_surf_array[ctop:cbottom, cleft:cright, :] = new_colors
        """
        cond = (canvas_surf_array[:, :, 3]!=255)
        cond_multi = numpy.repeat(cond, 4)
        cond_multi.shape = (cond.shape[0], cond.shape[1], 4)
        filled_values = numpy.repeat([[255, 0, 0, 255]], height*width, axis=0 ).astype(numpy.uint8)
        filled_values.shape= (cond.shape[0], cond.shape[1], 4)
        canvas_surf_array = numpy.where(cond_multi, filled_values, canvas_surf_array)
        """
        canvas = cairo.ImageSurface.create_for_data(
                canvas_surf_array, cairo.FORMAT_ARGB32, canvas_width, canvas_height)

        if scale != 1:
            enlarged_canvas = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(enlarged_canvas)
            ctx.rectangle(0, 0, width, height)
            ctx.scale(1./scale, 1./scale)
            ctx.set_source_surface(canvas)
            ctx.paint()
            canvas = enlarged_canvas
        return canvas

    def draw(self, ctx, border_color, border_width):
        for object_3d in self.sorted_items:
            object_3d.draw(ctx, self, border_color=border_color, border_width=border_width)


    def get_image_canvas_high_quality(self,
            container,
            canvas_width, canvas_height, premat,
            left, top, width, height,
            border_color=None, border_width=None):
        min_depth = -100000

        canvas_width = int(canvas_width)
        canvas_height = int(canvas_height)
        canvas_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, canvas_width, canvas_height)
        ctx = cairo.Context(canvas_surf)
        ctx.rectangle(0, 0, canvas_width, canvas_height)
        draw_fill(ctx, "00000000")
        canvas_surf_array = surface2array(canvas_surf)

        canvas_z_depths = numpy.zeros(canvas_surf_array.shape[:2], dtype="f")
        canvas_z_depths.fill(min_depth)

        canvas_normals = numpy.zeros(
            (canvas_surf_array.shape[0],
             canvas_surf_array.shape[1],
             3), dtype="f")
        canvas_normals.fill(0)

        canvas_points = numpy.zeros(
            (canvas_surf_array.shape[0],
             canvas_surf_array.shape[1],
             3), dtype="f")
        canvas_points.fill(0)

        invert = cairo.Matrix().multiply(premat)
        invert.invert()
        xx, yx, xy, yy, x0, y0 = invert
        numpy_pre_invert_mat = numpy.array([[xx, xy, x0], [yx, yy, y0]])

        span_y = max(-top, top+height)
        lights = container.get_lights()
        lights = sorted(lights, self.z_depth_sort_key)

        for object_3d in self.sorted_items:
            brect = object_3d.bounding_rect[self]
            bleft, btop = brect[0][0], brect[0][1]
            bright, bbottom = brect[1][0], brect[1][1]

            if bleft>left+width or bright<left or \
               btop>span_y or bbottom<-span_y:
                continue

            sleft = max(left, bleft)
            stop = btop#max(top, btop)
            sright = min(left+width, bright+1)
            sbottom = bbottom#min(top+height, bbottom+1)

            sw = sright-sleft
            sh = sbottom-stop

            if sw<=0 or sh<=0:
                continue

            poly_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, canvas_width, canvas_height)
            poly_ctx = cairo.Context(poly_surf)
            set_default_line_style(poly_ctx)
            poly_ctx.rectangle(0, 0, canvas_width, canvas_height)
            poly_ctx.set_source_rgba(1, 0, 0, 0)
            poly_ctx.fill()
            poly_ctx.set_matrix(premat)
            object_3d.draw(poly_ctx, self, border_color=border_color, border_width=border_width)
            del poly_ctx

            surfacearray = surface2array(poly_surf)

            xs = numpy.arange(0, canvas_width, step=1)
            xcount = len(xs)
            ys = numpy.arange(0, canvas_height, step=1)
            ycount = len(ys)
            xs, ys = numpy.meshgrid(xs, ys)
            surface_grid = numpy.vstack((xs.flatten(), ys.flatten(), numpy.ones(xcount*ycount)))
            surface_grid.shape = (3, ycount*xcount)
            del xs, ys

            hit_area_cond = (surfacearray[:, :, 3]>self.hit_alpha)
            hit_area_cond.shape = (ycount*xcount,)

            canvas_poly_coords = surface_grid[:, hit_area_cond]
            canvas_poly_coords.shape = (3, -1)
            del hit_area_cond

            poly_coor_x = canvas_poly_coords[0, :].astype(numpy.uint32)
            poly_coor_y = canvas_poly_coords[1, :].astype(numpy.uint32)

            coords = numpy.matmul(numpy_pre_invert_mat, canvas_poly_coords)
            coords.shape = (2, -1)

            del canvas_poly_coords

            coords_depths = numpy.matmul(object_3d.plane_params_normalized[self],
                numpy.concatenate((coords, [numpy.ones(coords.shape[1])]), axis=0))

            surface_points = numpy.concatenate((coords, [coords_depths]), axis=0).T
            del coords

            canvas_points[poly_coor_y, poly_coor_x, :] = surface_points
            canvas_normals[poly_coor_y, poly_coor_x, :] = object_3d.plane_normals[self].copy()

            pre_depths = canvas_z_depths[poly_coor_y, poly_coor_x]
            depths_cond = pre_depths<coords_depths

            new_depths = numpy.where(depths_cond, coords_depths, pre_depths)
            canvas_z_depths[poly_coor_y, poly_coor_x] = new_depths
            del pre_depths, new_depths

            pre_colors = canvas_surf_array[poly_coor_y, poly_coor_x, :]
            pre_colors.shape = (-1, 4)

            depths_cond_multi = numpy.repeat(depths_cond, 4)
            depths_cond_multi.shape = (depths_cond.shape[0], 4)

            picked_surface = surfacearray[poly_coor_y, poly_coor_x]
            picked_surface.shape = (-1, 4)

            for light in lights:
                light_depths_cond = ((coords_depths<light.z_depths[self]) & (coords_depths>min_depth))

                light_vectors = light.rel_location_values[self][0][:3]-surface_points[light_depths_cond, :]
                if len(light_vectors)==0:
                    continue
                surface_normals = object_3d.plane_normals[self]

                norm = numpy.linalg.norm(light_vectors, axis=1)
                norm = numpy.repeat(norm, 3)
                norm.shape = (-1,3)
                light_vectors = light_vectors/norm

                cosines = numpy.sum(light_vectors*surface_normals, axis=1)
                cosines = numpy.abs(cosines)

                cosines_multi = numpy.repeat(cosines, 4)
                cosines_multi.shape = (cosines.shape[0],4)

                if hasattr(light, "normal"):
                    cosines = numpy.sum(-light_vectors*light.normal.values[:3], axis=1)
                    cosines = numpy.abs(cosines)
                    damp = numpy.exp(-light.decay*(numpy.abs(cosines-light.cone_cosine)))
                    colors = numpy.repeat([light.color.to_255()], len(light_vectors), axis=0)
                    colors.shape = (-1, 4)
                    colors[:,3] = colors[:,3]*cosines
                else:
                    colors = numpy.repeat([light.color.to_255()], len(light_vectors), axis=0)

                pre_surf_colors = picked_surface[light_depths_cond, :].copy()
                picked_surface[light_depths_cond, :] = (pre_surf_colors*(1-cosines_multi) + \
                    colors*cosines_multi).astype(numpy.uint8)

            new_colors = numpy.where(depths_cond_multi, picked_surface, pre_colors)
            new_colors.shape = (-1, 4)
            del depths_cond_multi, pre_colors, picked_surface

            canvas_surf_array[poly_coor_y, poly_coor_x, :] = new_colors

            del poly_coor_x, poly_coor_y

        if self.convolve_kernel:
            n=self.convolve_kernel
            kernel = numpy.ones(n*n).reshape(n,n)*1./(n*n)
            for i in xrange(4):
                canvas_surf_array[:,:,i] = ndimage.convolve(
                    canvas_surf_array[:,:,i], kernel, mode="constant")

        if self.hsv_coef:
            hsv = rgb_to_hsv(canvas_surf_array[:,:,:3].copy())
            hsv[:, :, 0] = (hsv[:, :,0]*self.hsv_coef[0])
            hsv[:, :, 1] = (hsv[:, :,1]*self.hsv_coef[1])
            hsv[:, :, 2] = (hsv[:, :,2]*self.hsv_coef[2])
            canvas_surf_array[:, :, :3] = hsv_to_rgb(hsv)

        """
        for light in lights:
            depths_cond = ((canvas_z_depths<light.z_depths[self]) & (canvas_z_depths>min_depth))

            light_vectors = light.rel_location_values[self][0][:3]-canvas_points[depths_cond, :]
            if len(light_vectors)==0:
                continue
            surface_normals = canvas_normals[depths_cond, :]

            norm = numpy.linalg.norm(light_vectors, axis=1)
            norm = numpy.repeat(norm, 3)
            norm.shape = (-1,3)
            light_vectors = light_vectors/norm

            cosines = numpy.sum(light_vectors*surface_normals, axis=1)
            cosines = numpy.abs(cosines)

            cosines_multi = numpy.repeat(cosines, 4)
            cosines_multi.shape = (cosines.shape[0],4)

            if hasattr(light, "normal"):
                cosines = numpy.sum(-light_vectors*light.normal.values[:3], axis=1)
                cosines = numpy.abs(cosines)
                damp = numpy.exp(-light.decay*(numpy.abs(cosines-light.cone_cosine)))
                cosines = numpy.where(cosines<light.cone_cosine, damp, 1)
                colors = numpy.repeat([light.color.to_255()], len(light_vectors), axis=0)
                colors.shape = (-1, 4)
                colors[:,3] = colors[:,3]*cosines

            else:
                colors = numpy.repeat([light.color.to_255()], len(light_vectors), axis=0)

            pre_colors = canvas_surf_array[depths_cond, :].copy()
            canvas_surf_array[depths_cond, :] = (pre_colors*(1-cosines_multi) + \
                colors*cosines_multi).astype(numpy.uint8)
        """
        canvas = cairo.ImageSurface.create_for_data(
               numpy.getbuffer(canvas_surf_array), cairo.FORMAT_ARGB32, canvas_width, canvas_height)
        return canvas

    def draw_objects(self, ctx, left, top, width, height):
        image_canvas = self.get_image_canvas(left, top, width, height)
        ctx.set_source_surface(image_canvas, left, top)
        ctx.get_source().set_filter(cairo.FILTER_FAST)
        ctx.paint()
        """
        for object_3d in self.get_sorted_items():
            object_3d.draw_bounding_rect(self, ctx)
        """
