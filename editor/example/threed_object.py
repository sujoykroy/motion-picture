from gi.repository import Gtk, Gdk
from MotionPicture.commons  import *
import numpy

DEG2RAD = math.pi/180.

class Viewer(Gtk.Window):
    def __init__(self, width=400, height=300):
        super(Viewer, self).__init__()
        self.set_size_request(width, height)
        self.connect("delete-event", self.quit)
        self.set_position(Gtk.WindowPosition.CENTER)


        self.root_box = Gtk.VBox()
        self.add(self.root_box)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_events(
            Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK|\
            Gdk.EventMask.BUTTON_RELEASE_MASK|Gdk.EventMask.SCROLL_MASK)
        self.drawing_area.connect("draw", self.on_drawing_area_draw)
        self.drawing_area.connect("button-press-event", self.on_drawing_area_mouse_press)
        self.drawing_area.connect("button-release-event", self.on_drawing_area_mouse_release)
        self.drawing_area.connect("motion-notify-event", self.on_drawing_area_mouse_move)
        self.drawing_area.connect("scroll-event", self.on_drawing_area_mouse_scroll)
        self.root_box.pack_start(self.drawing_area, expand=True, fill=True, padding=0)

        self.move_control_box = Gtk.Grid()
        self.allowed_moves = set()
        move_items = ["ctx cty ctz crx cry crz".split(" "),
                      "otx oty otz orx ory orz".split(" "),
                      "os".split(" ")]
        for i in range(len(move_items)):
            for j in range(len(move_items[i])):
                check_button = Gtk.CheckButton.new_with_label(move_items[i][j])
                check_button.connect("toggled", self.move_check_button_clicked, move_items[i][j])
                self.move_control_box.attach(check_button, left=j, top=i, width=1, height=1)
        self.root_box.pack_start(self.move_control_box, expand=False, fill=False, padding=0)

        self.d3_objects = Container3d()
        minimalistic =  not True
        if not minimalistic:
            cube = PolyGroup3d.create_from_polygons_points(
                kind="linear",
                polygons_points = [
                    ((0, 0, 0), (30, 0, 0), (30, 30, 0), (0, 30, 0)),
                    ((0, 0, 0), (0, 0, 30), (30, 0, 30), (30, 0, 0)),
                    ((0, 0, 0), (0, 0, 30), (0, 30, 30), (0, 30, 0)),

                    ((0, 0, 30), (30, 0, 30), (30, 30, 30), (0, 30, 30)),
                    ((0, 30, 0), (0, 30, 30), (30, 30, 30), (30, 30, 0)),
                    ((30, 0, 0), (30, 0, 30), (30, 30, 30), (30, 30, 0)),
                ]
            )
            cube.polygons[0].fill_color="D734FF"
            cube.polygons[3].fill_color="FFD734"
            #cube.rotate_deg((30, 0, 0))
            #cube.scale.multiply(2)
            #cube.translate((0,20,0))
            self.d3_objects.append(cube)

        #"""
        cube2 = PolyGroup3d(
            points = (
                (0, 0, 0), (30, 0, 0), (30, 30, 0), (0, 30, 0),
                (0, 0, 30), (30, 0, 30), (30, 30, 30), (0, 30, 30)),
            polygons = [
                (0, 3, 7, 4)#,(0, 1, 2, 3),
            ]
        )
        cube2.translate((0, 50, 0))
        self.d3_objects.append(cube2)
        #"""
        self.moveable_obj = self.d3_objects
        filename = "/home/sujoy/Temporary/batman hero182.dae"
        filename = "/home/sujoy/Downloads/3dModels/low-poly-island.dae"
        filename1 = "/home/sujoy/Downloads/3dModels/test.dae"
        if True:
            external_obj = Container3d()
            external_obj.load_from_file(filename)
            #external_obj.translate((50, 0, 100))
            self.d3_objects.append(external_obj)
            external_obj.scale.multiply(100)
            #self.moveable_obj = external_obj

        #external_obj.translation.assign(0,0,0)
        #self.d3_objects[-2].scale.multiply(10)
        #self.d3_objects[-2].rotate_deg((0, 0, 150))
        #self.d3_objects["Geometry"].border_width=0
        #self.d3_objects["Sphere"].translate((100, 0, 0))
        #self.d3_objects["Sphere"].scale.multiply(50)
        """
        phi_count = 10
        theta_count = 3
        r = 200
        for iphi in range(phi_count):
            phi = iphi*360./phi_count
            for itheta in range(theta_count):
                theta = itheta*180./(theta_count*DEG2PI)
                x = r*math.sin(theta)*math.cos(phi)
                y = r*math.sin(theta)*math.sin(phi)
                z = r*math.cos(theta)
                if self.d3_objects:
                    new_cube = cube.copy()
                else:
                    new_cube = cube
                new_cube.translation.assign(x, y, z)
                self.d3_objects.append(new_cube)
        """

        """
        curved3d = PolyGroup3d(
            kind="quadratic",
            border_width=5,
            force_style=True,
            polygons = [
                Polygon3d(
                    is_line=not True, fill_color="FF0000",
                    points=(
                        (0, 0, 0), (100, 20, 30), (50, 30, 60), (40, 100, 50),
                        (20, 40, 70), (150, 130, 90), (-30,0, 0),
                        (-20, -40, -70), (-50, -30, 90), (0,0, 0)
                    ), closed=False),
            ]
        )
        curved3d.translate((60, 60, 60))
        self.d3_objects.append(curved3d)
        """
        if not minimalistic and False:
            self.d3_objects.append(PolyGroup3d.create_polygon(
                points = ((0, 0, 0), (200, 0, 0)), border_color="FF0000"))
            self.d3_objects.append(PolyGroup3d.create_polygon(
                points = ((0, 0, 0), (0, 200, 0)), border_color="00FF00"))
            self.d3_objects.append(PolyGroup3d.create_polygon(
                points = ((0, 0, 0), (0, 0, 200)), border_color="0000FF"))


        """
        line1 = PolyGroup3d.create_polygon(
                points = ((0, 0, 0), (200, 0, 0)), border_color="FF0000")
        line2 = PolyGroup3d.create_polygon(
                points = ((0, 0, 0), (200, 0, 0)), border_color="00FF00")
        self.d3_objects.append(line1)
        new_d3_ob = Container3d()
        self.d3_objects.append(new_d3_ob)
        new_d3_ob.append(line2)
        """

        #self.d3_objects.append(self.d3_objects[0].copy())
        #self.d3_objects[-1].translate((50, 0, 0))

        self.cameras = []
        self.cameras.append(Camera3d())

        #self.cameras[0].viewer.translate((0, 0, 0*1/math.tan(105*.5)))
        #self.cameras[0].translate((50, 50, 50))
        self.cameras[0].rotate_deg((-120, 0, -20))
        #self.cameras[0].rotate_deg((50, 0, 90))

        self.d3_objects.precalculate()
        self.cameras[0].precalculate()
        self.d3_objects.build_projection(self.cameras[0])
        self.cameras[0].sort_items()

        self.scroll_type = "rz"
        self.show_all()

        self.mouse_point = Point(0, 0)
        self.mouse_press_start_point = Point(0, 0)
        self.selected_point_index =  None

        imgf = "/home/sujoy/.Vds/muspic/ms.png"
        self.uvmap_scale = 0

    def move_check_button_clicked(self, widget, move_name):
        if widget.get_active():
            self.allowed_moves.add(move_name)
        else:
            self.allowed_moves.remove(move_name)

    def on_drawing_area_mouse_scroll(self, widget, event):
        if event.direction == Gdk.ScrollDirection.UP:
            direction = 1.
        elif event.direction == Gdk.ScrollDirection.DOWN:
            direction = -1.

        if "crx" in self.allowed_moves:
            self.cameras[0].rotate_deg((direction, 0, 0))
        if "cry" in self.allowed_moves:
            self.cameras[0].rotate_deg((0, direction, 0))
        if "crz" in self.allowed_moves:
            self.cameras[0].rotate_deg((0, 0, direction))

        if "ctx" in self.allowed_moves:
            self.cameras[0].translate((direction, 0, 0))
        if "cty" in self.allowed_moves:
            self.cameras[0].translate((0, direction, 0))
        if "ctz" in self.allowed_moves:
            self.cameras[0].translate((0, 0, direction))

        if "orx" in self.allowed_moves:
            self.moveable_obj.rotate_deg((direction, 0, 0))
        if "ory" in self.allowed_moves:
            self.moveable_obj.rotate_deg((0, direction, 0))
        if "orz" in self.allowed_moves:
            self.moveable_obj.rotate_deg((0, 0, direction))

        if "otx" in self.allowed_moves:
            self.moveable_obj.translate((direction, 0, 0))
        if "oty" in self.allowed_moves:
            self.moveable_obj.translate((0, direction, 0))
        if "otz" in self.allowed_moves:
            self.moveable_obj.translate((0, 0, direction))

        if "os" in self.allowed_moves:
            self.moveable_obj.scale.multiply(1+direction*.1)

        if any(m[0]=="o" for m in self.allowed_moves):
            self.moveable_obj.precalculate()
        self.cameras[0].precalculate()
        self.d3_objects.build_projection(self.cameras[0])
        self.cameras[0].sort_items()
        self.drawing_area.queue_draw()

    def on_drawing_area_draw(self, widget, ctx):
        ww = widget.get_allocated_width()
        wh = widget.get_allocated_height()
        set_default_line_style(ctx)
        ctx.set_antialias(False)
        #ctx.rectangle(0, 0, ww, wh)
        #draw_fill(ctx, "FFFFFF")
        #ctx.save()
        #ctx.rectangle(10, 10, 10, 10)
        #ctx.clip()
        #ctx.rectangle(12, 12, 30, 30)
        #draw_fill(ctx, "FFFF00")
        #draw_stroke(ctx, 1, "000000")
        #ctx.restore()

        ctx.translate(ww*.5, wh*.5)
        #ctx.scale(1, -1)
        #ctx.rectangle(10, 10, 10, 10)
        #ctx.clip()
        self.cameras[0].draw_objects(ctx, -ww*.5, -wh*.5, width=ww, height=wh)
        return
        self.cameras[0].build_grid(ctx,
            left=-ww*.5, top=-wh*.5, width=ww, height=wh)
        return
        self.cameras[0].draw_overlapped_objects(ctx,
            left=-ww*.5, top=-wh*.5, width=ww, height=wh)

        return
        x_count = ww/2
        y_count = 2
        x_step = ww*1.0/x_count
        y_step = wh*1.0/y_count
        for xc in range(x_count):
            for yc in range(y_count):
                x1 = -ww*.5+xc*x_step
                y1 = -wh*.5+yc*y_step
                x2 = x1+x_step
                y2 = y1+y_step
                x1 -= 1
                x2 += 1
                y1 -= 1
                y2 += 1
                ctx.save()
                ctx.rectangle(x1, y1, x2-x1, y2-y1)
                ctx.clip()
                #self.cameras[0].draw_objects_inside(ctx, x1,y1,x2,y2)
                ctx.restore()

    def on_drawing_area_mouse_move(self, widget, event):
        self.mouse_point.copy_from(event)
        return
        if self.selected_point_index is not None:
            ww = widget.get_allocated_width()
            wh = widget.get_allocated_height()
            mouse_camera_point = numpy.array([self.mouse_point.x-ww*.5, self.mouse_point.y-wh*.5])
            diff_point = self.mouse_point.diff(self.mouse_press_start_point)
            if diff_point.x>0 or diff_point.y<0:
                incre = 1
            else:
                incre = -1
            #self.selected_point.set_x(self.selected_point.get_x()+diff_point.x)
            self.selected_point.values = self.cameras[0].reverse_project_point_value(
                mouse_camera_point,
                self.selected_point_camera_values[2])
            object3d = self.d3_objects[1]
            object3d.build_projection(self.cameras[0])
            self.queue_draw()

    def on_drawing_area_mouse_press(self, widget, event):
        return
        ww = widget.get_allocated_width()
        wh = widget.get_allocated_height()
        mouse_camera_point = numpy.array([self.mouse_point.x-ww*.5, self.mouse_point.y-wh*.5])
        self.mouse_press_start_point.copy_from(self.mouse_point)
        object3d = self.d3_objects[1]
        self.selected_point_index = object3d.get_point_index_at(
                self.cameras[0], mouse_camera_point)
        if self.selected_point_index is not None:
            self.selected_point = object3d.points[self.selected_point_index]
            self.selected_point_init_projection = object3d.get_point_projection(
                        self.cameras[0], self.selected_point_index)
            self.selected_point_camera_values = self.cameras[0].forward_transform_point_values(
                            self.selected_point.values)

    def on_drawing_area_mouse_release(self, widget, event):
        self.selected_point_index = None

    def quit(self, widget, event):
        Gtk.main_quit()

viewer = Viewer()
Gtk.main()
