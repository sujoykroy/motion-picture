import numpy, cairo, math

from object3d import Object3d
from point3d import Point3d
from polygon3d import Polygon3d

def surface2array(surface):
    data = surface.get_data()
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

    def project_point_values(self, point_values):
        point_values = self.forward_transform_point_values(point_values)
        return self.viewer_point_values(point_values)

    def viewer_point_values(self, point_values):
        if self.viewer.get_z() != 0:
            ratio = self.viewer.get_z()/point_values[:, 2]
            x_values = (ratio*point_values[:,0]) - self.viewer.get_x()
            y_values = (ratio*point_values[:,1]) - self.viewer.get_y()
            return numpy.stack((x_values, y_values), axis=1)#reverse xy
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

    def get_sorted_items(self):
        for i in range(len(self.sorted_items)):
            yield self.sorted_items[i]

    def sort_items(self):
        self.sorted_items = sorted(Polygon3d.Items, self.z_depth_sort_key)
        self.poly_face_params = None
        for item in self.sorted_items:
            params = numpy.array([item.plane_params_normalized[self]])
            if self.poly_face_params is None:
                self.poly_face_params = params
            else:
                self.poly_face_params = numpy.concatenate(
                        (self.poly_face_params, params), axis=0)
        """
        self.intersect_rects = []
        tolerance = 1.
        for i in range(len(self.sorted_items)):
            item1 = self.sorted_items[i]
            #print item1.z_depths[self]
            for j in range(i+1, len(self.sorted_items)):
                item2 = self.sorted_items[j]
                if item1.z_depths[self] != item2.z_depths[self]:
                    continue
                rect = item1.get_intersect_rect(self, item2)
                if rect is None:
                    continue
                if abs(rect[0][0]-rect[1][0])<tolerance or \
                   abs(rect[0][1]-rect[1][1])<tolerance:
                    continue

                self.intersect_rects.append(rect)
        """
        #self.sorted_items = reversed(self.sorted_items)
        return
        print "\n\n"
        for object_3d in self.get_sorted_items():
            print "poly", object_3d.id_num, "z-depth", object_3d.z_depths[self]
            #print object_3d.get_camera_points(self)
            #print object_3d.point_indices

    def z_depth_sort_key(self, o1, o2):
        ps1 = o1.z_depths[self]
        ps2 = o2.z_depths[self]
        if ps1>ps2:
            return -1
        if ps1 == ps2:
            return 0
        return 1

    def draw_objects(self, ctx, left, top, width, height):
        pixel_count = width*height
        max_depth = 100000

        canvas_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        canvas_surf_array = surface2array(canvas_surf)

        canvas_z_depths =numpy.repeat(max_depth, pixel_count)
        canvas_z_depths = canvas_z_depths.astype("f").reshape((height, width))

        pad = 3
        for object_3d in self.get_sorted_items():
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

            cleft = int(sleft-left)
            cright = int(sright-left)
            ctop = int(stop-top)
            cbottom = int(sbottom-top)

            poly_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
            poly_ctx = cairo.Context(poly_surf)
            poly_ctx.rectangle(0, 0, sw, sh)
            poly_ctx.set_source_rgba(1, 0, 0, 0)
            poly_ctx.fill()
            poly_ctx.translate(-bleft-(sleft-bleft), -btop-(stop-btop))
            object_3d.draw(poly_ctx, self)

            surfacearray = surface2array(poly_surf)
            area_cond = (surfacearray[:, :, 3]!=255)

            xs = numpy.arange(sleft, sright)
            xcount = len(xs)
            ys = numpy.arange(stop, sbottom)
            ycount = len(ys)
            xs, ys = numpy.meshgrid(xs, ys)
            coords = numpy.vstack((xs.flatten(), ys.flatten()))
            coords = coords.T#.reshape((ycount, xcount, 2))
            coords.shape = (xcount*ycount, 2)

            coords_depths = numpy.matmul(object_3d.plane_params_normalized[self],
                numpy.concatenate((coords.T, [numpy.ones(coords.shape[0])]), axis=0))
            coords_depths.shape = (ycount, xcount)
            blank_depths = numpy.repeat(max_depth+1, ycount*xcount)
            blank_depths.shape = coords_depths.shape
            coords_depths = numpy.where(area_cond, blank_depths, coords_depths)

            pre_depths = canvas_z_depths[ctop:cbottom, cleft:cright]
            pre_depths.shape = (cbottom-ctop, cright-cleft)
            depths_cond = pre_depths>coords_depths

            new_depths = numpy.where(depths_cond, coords_depths, pre_depths)
            canvas_z_depths[ctop:cbottom, cleft:cright] = new_depths

            pre_colors = canvas_surf_array[ctop:cbottom, cleft:cright, :]
            pre_colors.shape = (cbottom-ctop, cright-cleft, 4)

            depths_cond_multi = numpy.repeat(depths_cond, 4)
            depths_cond_multi.shape = (depths_cond.shape[0], depths_cond.shape[1], 4)

            new_colors = numpy.where(depths_cond_multi, surfacearray, pre_colors)
            canvas_surf_array[ctop:cbottom, cleft:cright, :] = new_colors
        cond = (canvas_surf_array[:, :, 3]!=255)
        cond_multi = numpy.repeat(cond, 4)
        cond_multi.shape = (cond.shape[0], cond.shape[1], 4)
        filled_values = numpy.repeat([[255, 0, 0, 255]], height*width, axis=0 ).astype(numpy.uint8)
        filled_values.shape= (cond.shape[0], cond.shape[1], 4)
        canvas_surf_array = numpy.where(cond_multi, filled_values, canvas_surf_array)
        new_canvas_surf = cairo.ImageSurface.create_for_data(
                numpy.getbuffer(canvas_surf_array), cairo.FORMAT_ARGB32, width, height)
        ctx.set_antialias(True)
        ctx.set_source_surface(new_canvas_surf, left, top)
        ctx.get_source().set_filter(cairo.FILTER_FAST)
        ctx.paint()
        return
        for object_3d in self.get_sorted_items():
            object_3d.draw_bounding_rect(self, ctx)

    def build_grid(self, ctx, left, top, width, height):
        x_values = numpy.arange(left, left+width, dtype="f")
        y_values = numpy.arange(top, top+height, dtype="f")
        x_values, y_values = numpy.meshgrid(x_values, y_values)
        x_values = x_values.flatten()
        y_values = y_values.flatten()
        pixel_count = x_values.shape[0]
        xyvalues = numpy.vstack((x_values, y_values, numpy.ones(x_values.shape[0], dtype="f")))
        x_values = None
        y_values = None
        self.poly_grid_depths = numpy.matmul(self.poly_face_params, xyvalues)
        far_values = numpy.repeat(1000000, pixel_count).astype("f")
        for s in range(len(self.sorted_items)):
            item = self.sorted_items[s]
            brect = item.bounding_rect[self]

            screen = numpy.zeros(pixel_count, dtype="bool")
            screen.shape = (width, height)
            screen[int(brect[0][0]):int(brect[0][1])+1,int(brect[1][0]):int(brect[1][1])+1] = True
            screen.shape = (pixel_count,)
            self.poly_grid_depths[s] = numpy.where(screen,self.poly_grid_depths[s], far_values)
        self.poly_grid_depths_index = numpy.argmin(self.poly_grid_depths, axis=0)
        #print numpy.unique(self.poly_grid_depths_index)
        print numpy.unique(self.poly_grid_depths_index)
        #print self.poly_face_params

    def draw_overlapped_objects(self, ctx, left, top, width, height):
        x_count = 10
        y_count = x_count
        x_step = width*1.0/x_count
        y_step = height*1.0/y_count
        for xc in range(x_count):
            for yc in range(y_count):
                x1 = left+xc*x_step
                y1 = top+yc*y_step
                x2 = x1+x_step
                y2 = y1+y_step
                x1 -= 1
                x2 += 1
                y1 -= 1
                y2 += 1
                for rect in self.intersect_rects:
                    if x2<rect[0][0] or x1>rect[1][0]:
                        continue
                    if y1>rect[1][1] or y2<rect[0][1]:
                        continue
                    ctx.save()
                    ctx.rectangle(x1, y1, x2-x1, y2-y1)
                    #draw_stroke(ctx, 1, "dddddd")
                    ctx.clip()
                    self.draw_objects_inside(ctx, x1,y1,x2,y2)
                    ctx.restore()
                    continue
                    for nx1 in range(int(x1), int(x2), 1):
                        for ny1 in range(int(y1), int(y2), 1):
                            ctx.save()
                            ctx.rectangle(nx1, ny1, 1, 1)
                            #draw_stroke(ctx, 1, "dddddd")
                            ctx.clip()
                            self.draw_objects_inside(ctx, x1,y1,x2,y2)
                            ctx.restore()
                    break

    def draw_objects_inside(self, ctx, x1,y1,x2,y2):
        midx = (x1+x2)*.5
        midy = (y1+y2)*.5
        def z_depth_sort_key(o1, o2):
            z1 = o1.get_z_cut(self, midx, midy)
            z2 = o2.get_z_cut(self, midx, midy)
            if z1>z2:
                return -1
            if z1 == z2:
                return 0
            return 1
        items = sorted(Polygon3d.Items, z_depth_sort_key)
        for object_3d in items:
            object_3d.draw(ctx, self)
