from polygon3d_gl_drawer import Polygon3DGLDrawer
import ctypes
from OpenGL.GL import *
from misc import *

class ThreeDGLRenderContext(object):
    def __init__(self):
        self.drawer = Polygon3DGLDrawer();
        self.texture_handle_maps = dict()

    def get_texture_handle(resource_name):
        if (resource_name not in self.texture_handle_maps):
            self.load_texture_from_file(resource_name)
        return self.texture_handle_maps[resource_name][0]

    def cleanup(self):
        for texture_handles in self.texture_handle_maps.values():
            glDeleteTextures(1, texture_handles)
        self.drawer.cleanup()

    def get_drawer(self):
        return self.drawer

    def load_texture_from_file(resource_name):
        texture_handles = glGenTextures(1)

        bitmap = ImageHelper.get_bitmap_data_from_file(resource_name)

        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, texture_handles[0]);

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, bitmap.shape[1],
                 bitmap.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE,
                 np.reshape(bitmap, (-1)))

        del bitmap
        self.texture_handle_maps[resource_name]= texture_handles

