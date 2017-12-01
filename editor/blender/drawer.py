import subprocess
import cairo
import os
import time
import imp

BLENDER_BIN_PATH = os.environ.get("MOTION_PICTURE_BLENDER_BIN_PATH", ".")
THIS_DIR = os.path.dirname(__file__)
SCRIPT_LOADER_FILEPATH = os.path.join(THIS_DIR, "script_loader.py")

def get_path_with_ext(path, ext):
    root, rem = os.path.splitext(path)
    if not rem:
        rem = ext
    return root+ext

class BlenderDrawer(object):
    def __init__(self, drawer_dir, temp_dir=None,
                       params_filename="blender_params.py",
                       blend_filename="blender.blend",
                       designer_filename="blender_designer.py"):
        self.params = dict()
        self.hidden_params = dict()
        self.progress = 0

        self.temp_dir = temp_dir
        self.image_filepath = "./blender_generated_image.png"
        if temp_dir is not None:
            for i in range(100):
                filepath = os.path.join(temp_dir, "blender_temp_{0}.png".format(time.time()))
                if not os.path.isfile(filepath):
                    self.image_filepath = filepath
                    break

        self.blend_filepath = os.path.join(drawer_dir,
                                        get_path_with_ext(blend_filename, ".blend"))
        self.designer_filepath = os.path.join(drawer_dir,
                                        get_path_with_ext(designer_filename, ".py"))
        self.params_filepath = os.path.join(drawer_dir,
                                        get_path_with_ext(params_filename, ".py"))
        self.blender_params = imp.load_source("blender_params",
                                        os.path.join(drawer_dir, params_filename))

        self.use_custom_surface = False
        self.image_surface = None
        self.params_info = dict()
        for key, item in self.blender_params.params_info.items():
            if item.get("hidden", False):
                continue
            self.params_info[key] = item

    def set_params(self, params):
        if params != self.params:
            self.params.update(params)
        self.image_surface = None

    def set_progress(self, value):
        self.progress = value
        self.image_surface = None

    def build_image(self):
        args = [BLENDER_BIN_PATH, "-b", self.blend_filepath,
                         "-P", SCRIPT_LOADER_FILEPATH,
                         "--",
                         "--params_filepath", self.params_filepath,
                         "--utils_folderpath", THIS_DIR,
                         "--image_filepath", self.image_filepath,
                         "--designer_filepath", self.designer_filepath,
                         "--progress", "{0}".format(self.progress)]
        for key in self.params_info.keys():
            value = self.params.get(key)
            if isinstance(value, float):
                value = "{0:f}".format(value)
            else:
                value = "{0}".format(value)
            args.extend(["--{0}".format(key), value])
        for key in self.hidden_params.keys():
            value = self.hidden_params.get(key)
            if isinstance(value, float):
                value = "{0:f}".format(value)
            else:
                value = "{0}".format(value)
            args.extend(["--{0}".format(key), value])

        #print(args)
        subprocess.call(args)
        self.image_surface = cairo.ImageSurface.create_from_png(self.image_filepath)

    def draw(self, ctx, anchor_at, width, height, parent_shape):
        if not self.image_surface:
            self.build_image()

        surface = self.image_surface
        ctx.rectangle(0, 0, width, height)
        sx = width*1./surface.get_width()
        sy = height*1./surface.get_height()
        if sx<1:
            ctx.translate(-(surface.get_width()-width)*.5, 0)
        if sy<1:
            ctx.translate(0, -(surface.get_height()-height)*.5)
        ctx.scale(sx , sy)
        ctx.set_source_surface(surface)
        ctx.paint()


