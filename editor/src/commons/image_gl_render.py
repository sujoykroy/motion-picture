from ctypes import *

import numpy, cairo
import OpenGL
from OpenGL.EGL import *
from OpenGL.GL import *

from threed_gl_render_context import ThreeDGLRenderContext

class ImageGLRender(object):
    RENDER_OBJECTS = dict()
    def checkEglError(self, msg):
        error = eglGetError()
        if error != EGL_SUCCESS:
            raise Exception(msg + ": EGL error: " + "{0}".format(error).decode("hex"))

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.threed_gl_render_context = None

        self.egl_display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
        if (self.egl_display == EGL_NO_DISPLAY):
            raise Exception("unable to get EGL14 display");

        major,minor = c_long(), c_long()

        if not eglInitialize(self.egl_display, major, minor):
            self.egl_display = None
            raise Exception("unable to initialize EGL14")
        print " major, minor",  major, minor
        #eglBindAPI(EGL_OPENGL_ES_API)

        attrib_list =  numpy.array([
                EGL_RED_SIZE, 8,
                EGL_GREEN_SIZE, 8,
                EGL_BLUE_SIZE, 8,
                EGL_ALPHA_SIZE, 8,
                EGL_DEPTH_SIZE, 16,
                EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
                EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
                EGL_NONE
        ], dtype="i4")
        configs = (EGLConfig*1)()
        numConfigs = c_long()
        if not eglChooseConfig(self.egl_display, attrib_list, configs, 1, numConfigs):
            raise Exception("unable to find RGB888+recordable ES2 EGL config")

        # Configure context for OpenGL ES 2.0.
        attrib_list =  numpy.array([
                EGL_CONTEXT_CLIENT_VERSION, 2,
                EGL_NONE
        ], dtype="i4")
        self.egl_context = eglCreateContext(self.egl_display, configs[0], EGL_NO_CONTEXT, attrib_list)
        print "self.egl_context", self.egl_context
        print "eglQueryAPI", eglQueryAPI()
        self.checkEglError("eglCreateContext")

        if self.egl_context is None:
            raise Exception("null context")

        #Create a pbuffer surface.
        surfaceAttribs = numpy.array([
                EGL_WIDTH, self.width,
                EGL_HEIGHT, self.height,
                EGL_NONE
        ], dtype="i4")
        self.egl_surface = eglCreatePbufferSurface(self.egl_display, configs[0], surfaceAttribs)
        self.checkEglError("eglCreatePbufferSurface");
        if self.egl_surface is None:
            raise Exception("surface was null")
        #self.initialize_surface()

    def __del__(self):
        if self.threed_gl_render_context:
            self.threed_gl_render_context.cleanup()
        eglMakeCurrent(self.egl_display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT)
        eglDestroySurface(self.egl_display, self.egl_surface)
        eglTerminate(self.egl_display)

    def initialize_surface(self):
        glEnable(GL_DEPTH_TEST)
        if self.threed_gl_render_context is None:
            self.threed_gl_render_context = ThreeDGLRenderContext()

    def draw_frame(self, pre_matrix, drawble):
        if not eglMakeCurrent(self.egl_display, self.egl_surface, self.egl_surface, self.egl_context):
            raise Exception("eglMakeCurrent failed")
        if not self.threed_gl_render_context:
            self.threed_gl_render_context = ThreeDGLRenderContext()
        glClearColor(.5, .5, .5, 0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        drawble.draw_gl(pre_matrix, self.threed_gl_render_context)

    def draw_and_get_image_surface(self, pre_matrix, drawable):
        self.draw_frame(pre_matrix, drawable)
        return self.get_image_surface()

    def toHex(self, s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '')
            if len(hv) == 1:
                hv = '0'+hv
            lst.append(hv)

        return reduce(lambda x,y:x+y, lst)

    def get_image_surface(self):
        pixels = numpy.zeros((self.height, self.width, 4), dtype=numpy.uint8)
        glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, array=pixels)
        print "pixel unique", numpy.unique(pixels)
        pixels = pixels[::-1,:, [2,1,0,3]]/255.
        pixels = pixels.astype(numpy.float32)
        #np_d_img = np_d_img[:,:,numpy.newaxis]
        pixels = numpy.ascontiguousarray(pixels)
        return cairo.ImageSurface.create_for_data(pixels, cairo.FORMAT_ARGB32, int(self.width), int(self.height))

    @classmethod
    def get_render(self, width, height):
        width = int(width)
        height = int(height)
        key = "{0}x{1}".format(width, height)
        if key not in ImageGLRender.RENDER_OBJECTS:
            ImageGLRender.RENDER_OBJECTS[key] = ImageGLRender(width, height)
        return ImageGLRender.RENDER_OBJECTS[key]

